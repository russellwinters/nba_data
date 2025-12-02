# NBA Data Cloud Hosting Planning Document

This document outlines options for hosting the NBA Data CLI application in the cloud to run on a schedule. It covers serverless solutions, containerized deployments, spot instances, and local hosting alternatives, with AWS as the preferred cloud provider.

---

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Hosting Options](#hosting-options)
  - [Option 1: AWS Lambda (Serverless)](#option-1-aws-lambda-serverless)
  - [Option 2: AWS ECS Fargate (Containerized Serverless)](#option-2-aws-ecs-fargate-containerized-serverless)
  - [Option 3: EC2 Spot Instances](#option-3-ec2-spot-instances)
  - [Option 4: Local Hosting with Cron Jobs](#option-4-local-hosting-with-cron-jobs)
- [Data Storage with S3](#data-storage-with-s3)
  - [S3 Bucket Structure](#s3-bucket-structure)
  - [Upload Strategy](#upload-strategy)
- [Tracking Previously Fetched Data](#tracking-previously-fetched-data)
  - [Option A: S3 Manifest File](#option-a-s3-manifest-file)
  - [Option B: DynamoDB State Table](#option-b-dynamodb-state-table)
  - [Option C: S3 Object Existence Check](#option-c-s3-object-existence-check)
- [Comparison Summary](#comparison-summary)
- [Recommendations](#recommendations)
- [Decisions](#decisions)
  - [Decision 1: MVP — Local Hosting with Cron Jobs](#decision-1-mvp--local-hosting-with-cron-jobs)
  - [Decision 2: Data Store Module with Progressive Storage](#decision-2-data-store-module-with-progressive-storage)
  - [Decision 3: Eventual Plan — Spot Instances with S3 Storage](#decision-3-eventual-plan--spot-instances-with-s3-storage)
  - [Decision 4: Fetch Tracking with Per-Module Timestamps](#decision-4-fetch-tracking-with-per-module-timestamps)
- [Implementation Roadmap](#implementation-roadmap)

---

## Overview

The NBA Data CLI currently runs on-demand to fetch data from the NBA Stats API. To maintain an up-to-date dataset, we need automated scheduled execution with:

1. **Scheduled execution**: Daily or more frequent runs during the NBA season
2. **Persistent storage**: Data stored in S3 for later retrieval
3. **Deduplication**: Track what has been fetched to avoid redundant API calls
4. **Cost efficiency**: Minimize infrastructure costs given sporadic workloads

---

## Requirements

| Requirement | Description |
|-------------|-------------|
| **Scheduling** | Run daily (or multiple times daily during season) |
| **Runtime** | Python 3.11+ with ~100MB of dependencies |
| **Execution Time** | 5-30 minutes depending on data scope |
| **Memory** | 256MB-1GB depending on data volume |
| **Storage** | Output CSV files to S3 |
| **State Tracking** | Log previously fetched data to prevent duplication |
| **Preferred Cloud** | AWS |

---

## Hosting Options

### Option 1: AWS Lambda (Serverless)

AWS Lambda provides fully managed, event-driven compute that scales automatically and charges only for execution time.

#### Architecture

```
EventBridge (Cron) → Lambda Function → S3 (Data Storage)
                          ↓
                    DynamoDB (State Tracking)
```

#### Configuration

```yaml
# serverless.yml (Serverless Framework example)
service: nba-data-fetcher

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  timeout: 900  # 15 minutes max
  memorySize: 512

functions:
  fetchPlayers:
    handler: handler.fetch_players
    events:
      - schedule: cron(0 6 * * ? *)  # Daily at 6 AM UTC
    environment:
      S3_BUCKET: nba-data-bucket
      
  fetchTeamGames:
    handler: handler.fetch_team_games
    events:
      - schedule: cron(0 7 * * ? *)  # Daily at 7 AM UTC
    environment:
      S3_BUCKET: nba-data-bucket

plugins:
  - serverless-python-requirements
```

#### Lambda Handler Example

```python
# handler.py
import os
import boto3
import json
from datetime import datetime
from lib.fetch_players import fetch_players

s3 = boto3.client('s3')

def fetch_players_handler(event, context):
    """Lambda handler for fetching players."""
    bucket = os.environ['S3_BUCKET']
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Fetch to local temp file
    local_path = '/tmp/players.csv'
    fetch_players(output_path=local_path)
    
    # Upload to S3
    s3_key = f'players/{today}/players.csv'
    s3.upload_file(local_path, bucket, s3_key)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'uploaded': s3_key})
    }
```

#### Pros

| Advantage | Description |
|-----------|-------------|
| **Zero infrastructure** | No servers to manage or patch |
| **Pay-per-use** | Only charged for actual execution time |
| **Auto-scaling** | Handles concurrent executions automatically |
| **Native scheduling** | EventBridge cron integration built-in |
| **Low cost** | Free tier includes 1M requests/month, 400,000 GB-seconds |

#### Cons

| Disadvantage | Description |
|--------------|-------------|
| **15-minute timeout** | Maximum execution time is 15 minutes |
| **Cold starts** | Initial invocation may have latency |
| **Package size limits** | 250MB unzipped deployment package |
| **Stateless** | No persistent local storage between invocations |
| **Complex dependencies** | May require Lambda layers for `nba_api` and `pandas` |

#### Cost Estimate

| Component | Monthly Cost (Est.) |
|-----------|---------------------|
| Lambda (512MB, 10min/day) | ~$0.50 |
| EventBridge | Free (up to 14M invocations) |
| S3 Storage (10GB) | ~$0.23 |
| S3 Requests | ~$0.05 |
| **Total** | **~$1/month** |

---

### Option 2: AWS ECS Fargate (Containerized Serverless)

ECS Fargate runs containers without managing EC2 instances, ideal for longer-running tasks that exceed Lambda's 15-minute limit.

#### Architecture

```
EventBridge (Cron) → ECS Fargate Task → S3 (Data Storage)
                          ↓
                    DynamoDB (State Tracking)
```

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "fetch.py"]
```

#### Task Definition

```json
{
  "family": "nba-data-fetcher",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "nba-data-fetcher",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/nba-data:latest",
      "essential": true,
      "environment": [
        {"name": "S3_BUCKET", "value": "nba-data-bucket"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nba-data-fetcher",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### EventBridge Rule

```json
{
  "Name": "nba-data-daily-fetch",
  "ScheduleExpression": "cron(0 6 * * ? *)",
  "State": "ENABLED",
  "Targets": [
    {
      "Id": "ecs-target",
      "Arn": "arn:aws:ecs:us-east-1:123456789:cluster/nba-cluster",
      "RoleArn": "arn:aws:iam::123456789:role/ecsEventsRole",
      "EcsParameters": {
        "TaskDefinitionArn": "arn:aws:ecs:us-east-1:123456789:task-definition/nba-data-fetcher:1",
        "LaunchType": "FARGATE",
        "NetworkConfiguration": {
          "awsvpcConfiguration": {
            "Subnets": ["subnet-xxx"],
            "AssignPublicIp": "ENABLED"
          }
        }
      }
    }
  ]
}
```

#### Pros

| Advantage | Description |
|-----------|-------------|
| **No time limit** | Tasks can run for hours if needed |
| **Container-based** | Same Docker image runs locally and in production |
| **No server management** | Fargate handles underlying infrastructure |
| **Flexible resources** | Scale CPU/memory independently |
| **Full Python ecosystem** | No package size limitations |

#### Cons

| Disadvantage | Description |
|--------------|-------------|
| **Higher minimum cost** | Pay for full task duration even if idle |
| **Cold start latency** | Container pull and startup adds ~30-60 seconds |
| **More complex setup** | Requires ECR, VPC, IAM configuration |
| **Networking required** | Must configure VPC and security groups |

#### Cost Estimate

| Component | Monthly Cost (Est.) |
|-----------|---------------------|
| Fargate (0.25 vCPU, 0.5GB, 15min/day) | ~$3.00 |
| ECR Storage | ~$0.10 |
| CloudWatch Logs | ~$0.50 |
| S3 Storage (10GB) | ~$0.23 |
| **Total** | **~$4/month** |

---

### Option 3: EC2 Spot Instances

EC2 Spot Instances provide up to 90% cost savings compared to on-demand pricing, ideal for fault-tolerant batch workloads.

#### Architecture

```
EventBridge → Lambda (Launcher) → EC2 Spot Instance → S3
                                        ↓
                              (Self-terminates after completion)
```

#### Launch Template

```json
{
  "LaunchTemplateName": "nba-data-fetcher",
  "LaunchTemplateData": {
    "ImageId": "ami-0abcdef1234567890",
    "InstanceType": "t3.micro",
    "IamInstanceProfile": {
      "Arn": "arn:aws:iam::123456789:instance-profile/nba-data-role"
    },
    "UserData": "base64-encoded-startup-script",
    "InstanceMarketOptions": {
      "MarketType": "spot",
      "SpotOptions": {
        "SpotInstanceType": "one-time",
        "InstanceInterruptionBehavior": "terminate"
      }
    }
  }
}
```

#### User Data Script

```bash
#!/bin/bash
set -e

# Install dependencies
yum update -y
yum install -y python3 python3-pip git

# Clone and setup
cd /home/ec2-user
git clone https://github.com/your-repo/nba_data.git
cd nba_data
pip3 install -r requirements.txt

# Run fetch
python3 fetch.py players --output /tmp/players.csv

# Upload to S3
aws s3 cp /tmp/players.csv s3://nba-data-bucket/players/$(date +%Y-%m-%d)/players.csv

# Self-terminate
shutdown -h now
```

#### Pros

| Advantage | Description |
|-----------|-------------|
| **Lowest cost** | Up to 90% cheaper than on-demand |
| **Full OS access** | Can install any software |
| **No time limits** | Run as long as needed |
| **Flexible instance types** | Choose optimal CPU/memory |

#### Cons

| Disadvantage | Description |
|--------------|-------------|
| **Interruption risk** | AWS can reclaim instances with 2-minute warning |
| **Complex orchestration** | Need Lambda or other service to launch instances |
| **Startup overhead** | Instance boot + setup takes 2-5 minutes |
| **More maintenance** | Need to maintain AMI or use user data scripts |
| **Spot availability** | Not guaranteed in all regions/AZs |

#### Cost Estimate

| Component | Monthly Cost (Est.) |
|-----------|---------------------|
| EC2 Spot (t3.micro, 15min/day) | ~$0.15 |
| Lambda Launcher | ~$0.01 |
| S3 Storage (10GB) | ~$0.23 |
| Data Transfer | ~$0.10 |
| **Total** | **~$0.50/month** |

---

### Option 4: Local Hosting with Cron Jobs

Traditional cron jobs on a local server or always-on machine (home server, Raspberry Pi, VPS).

#### Architecture

```
Cron Job → Python Script → Local Storage + S3 Sync
                ↓
          Local SQLite (State Tracking)
```

#### Crontab Configuration

```bash
# /etc/cron.d/nba-data-fetch

# Fetch players weekly on Sunday at 3 AM
0 3 * * 0 nba /home/nba/nba_data/scripts/fetch_and_sync.sh players

# Fetch team games daily at 6 AM
0 6 * * * nba /home/nba/nba_data/scripts/fetch_and_sync.sh team-games

# Fetch active player stats weekly
0 4 * * 0 nba /home/nba/nba_data/scripts/fetch_and_sync.sh player-stats
```

#### Fetch and Sync Script

```bash
#!/bin/bash
# scripts/fetch_and_sync.sh

set -e

cd /home/nba/nba_data
source .venv/bin/activate

DATA_TYPE=$1
DATE=$(date +%Y-%m-%d)
S3_BUCKET="nba-data-bucket"

# Load team list from config file (more maintainable than hardcoding)
# For production, consider: TEAMS=$(python -c "from lib.fetch_teams import get_team_abbreviations; print(' '.join(get_team_abbreviations()))")
TEAMS="ATL BOS BKN CHA CHI CLE DAL DEN DET GSW HOU IND LAC LAL MEM MIA MIL MIN NOP NYK OKC ORL PHI PHX POR SAC SAS TOR UTA WAS"

case $DATA_TYPE in
  "players")
    python fetch.py players --output data/players.csv
    aws s3 cp data/players.csv s3://$S3_BUCKET/players/$DATE/players.csv
    ;;
  "team-games")
    YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
    for TEAM in $TEAMS; do
      python fetch.py team-game-boxscores --team-id $TEAM --date $YESTERDAY --output data/${TEAM}_games.csv
      aws s3 cp data/${TEAM}_games.csv s3://$S3_BUCKET/team-games/$YESTERDAY/${TEAM}.csv
      sleep 3  # Rate limiting
    done
    ;;
  "player-stats")
    python fetch.py players --output data/players.csv
    # Additional logic to fetch active player stats
    ;;
esac

echo "$(date): Completed $DATA_TYPE fetch" >> /var/log/nba-data/fetch.log
```

**Note:** For production use, consider loading team abbreviations dynamically from the database or a configuration file instead of hardcoding them. This makes the script more maintainable when teams are added or relocated.

#### Pros

| Advantage | Description |
|-----------|-------------|
| **Full control** | Complete access to execution environment |
| **No cloud costs** | Only S3 storage costs if syncing |
| **Simple debugging** | Direct access to logs and state |
| **No cold starts** | Immediate execution |
| **Existing infrastructure** | May already have a suitable server |

#### Cons

| Disadvantage | Description |
|--------------|-------------|
| **Reliability** | Depends on local machine uptime |
| **Maintenance** | Must manage OS updates, power, network |
| **No auto-scaling** | Fixed resources |
| **Manual monitoring** | Need to set up alerting separately |
| **Single point of failure** | No built-in redundancy |

#### Cost Estimate

| Component | Monthly Cost (Est.) |
|-----------|---------------------|
| Local Server | $0 (if existing) or ~$5/month VPS |
| Electricity (if local) | ~$2-5/month |
| S3 Storage (10GB) | ~$0.23 |
| S3 Data Transfer | ~$0.10 |
| **Total** | **~$2-8/month** |

---

## Data Storage with S3

All hosting options should output data to Amazon S3 for centralized, durable storage that can be accessed by downstream consumers.

### S3 Bucket Structure

```
nba-data-bucket/
├── players/
│   └── 2024-01-15/
│       └── players.csv
├── teams/
│   └── 2024-01-15/
│       └── teams.csv
├── team-games/
│   └── 2024-01-15/
│       ├── LAL.csv
│       ├── GSW.csv
│       └── ...
├── player-games/
│   └── 2024-01-15/
│       └── 2544/
│           └── games.csv
├── player-stats/
│   └── 2024-01-15/
│       └── 2544/
│           └── career.csv
├── player-boxscores/
│   └── 0022400123/
│       └── boxscores.csv
└── _metadata/
    └── fetch_log.json
```

### Upload Strategy

#### Python S3 Upload Helper

```python
# lib/helpers/s3_upload.py
import boto3
import os
from datetime import datetime

def upload_to_s3(local_path: str, bucket: str, key_prefix: str) -> str:
    """
    Upload a local file to S3 with date partitioning.
    
    Args:
        local_path: Path to local file
        bucket: S3 bucket name
        key_prefix: Prefix for S3 key (e.g., 'players')
    
    Returns:
        S3 key of uploaded file
    """
    s3 = boto3.client('s3')
    
    today = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.basename(local_path)
    s3_key = f"{key_prefix}/{today}/{filename}"
    
    s3.upload_file(local_path, bucket, s3_key)
    
    return s3_key
```

#### S3 Bucket Policy (Example)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowFetcherWrite",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789:role/nba-data-fetcher-role"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::nba-data-bucket",
        "arn:aws:s3:::nba-data-bucket/*"
      ]
    }
  ]
}
```

#### S3 Lifecycle Policy

Configure lifecycle rules to manage storage costs:

```json
{
  "Rules": [
    {
      "ID": "TransitionToIA",
      "Status": "Enabled",
      "Filter": {},
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

---

## Tracking Previously Fetched Data

To avoid duplicate API calls and redundant processing, implement state tracking to log what data has already been fetched.

### Option A: S3 Manifest File

Store a JSON manifest file in S3 that tracks all completed fetches.

#### Implementation

```python
# lib/helpers/fetch_tracker_s3.py
import boto3
import json
from datetime import datetime
from typing import Optional

class S3FetchTracker:
    """Track fetch operations using an S3 manifest file."""
    
    def __init__(self, bucket: str, manifest_key: str = "_metadata/fetch_log.json"):
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.manifest_key = manifest_key
        self._manifest = None
    
    def _load_manifest(self) -> dict:
        """Load manifest from S3, or create empty one."""
        if self._manifest is None:
            try:
                response = self.s3.get_object(Bucket=self.bucket, Key=self.manifest_key)
                self._manifest = json.loads(response['Body'].read().decode('utf-8'))
            except self.s3.exceptions.NoSuchKey:
                self._manifest = {"fetches": []}
        return self._manifest
    
    def _save_manifest(self):
        """Save manifest back to S3."""
        self.s3.put_object(
            Bucket=self.bucket,
            Key=self.manifest_key,
            Body=json.dumps(self._manifest, indent=2),
            ContentType='application/json'
        )
    
    def is_fetched(self, entity_type: str, entity_id: str, date: str) -> bool:
        """Check if an entity has already been fetched for a given date."""
        manifest = self._load_manifest()
        for fetch in manifest["fetches"]:
            if (fetch["entity_type"] == entity_type and 
                fetch["entity_id"] == entity_id and 
                fetch["date"] == date):
                return True
        return False
    
    def mark_fetched(self, entity_type: str, entity_id: str, date: str, 
                     s3_key: str, record_count: int):
        """Record a completed fetch."""
        manifest = self._load_manifest()
        manifest["fetches"].append({
            "entity_type": entity_type,
            "entity_id": entity_id,
            "date": date,
            "s3_key": s3_key,
            "record_count": record_count,
            "fetched_at": datetime.utcnow().isoformat()
        })
        self._save_manifest()

# Usage example
tracker = S3FetchTracker(bucket="nba-data-bucket")

if not tracker.is_fetched("team-games", "LAL", "2024-01-15"):
    df = fetch_team_games(team_id="LAL", date="2024-01-15")
    s3_key = upload_to_s3(df, bucket, "team-games/2024-01-15/LAL.csv")
    tracker.mark_fetched("team-games", "LAL", "2024-01-15", s3_key, len(df))
```

#### Pros & Cons

| Pros | Cons |
|------|------|
| Simple implementation | File can grow large over time |
| No additional AWS services | Race conditions with concurrent writes |
| Easy to inspect and debug | Need to implement cleanup/rotation |

---

### Option B: DynamoDB State Table

Use DynamoDB for scalable, concurrent-safe state tracking.

#### Table Schema

```
Table: nba-data-fetch-log
Partition Key: entity_type#entity_id  (String)
Sort Key: fetch_date (String)

Attributes:
- s3_key (String)
- record_count (Number)
- fetched_at (String)
- status (String: "completed" | "failed")
```

#### Implementation

```python
# lib/helpers/fetch_tracker_dynamodb.py
import boto3
from datetime import datetime
from typing import Optional

class DynamoDBFetchTracker:
    """Track fetch operations using DynamoDB."""
    
    def __init__(self, table_name: str = "nba-data-fetch-log"):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
    
    def _make_pk(self, entity_type: str, entity_id: str) -> str:
        """Generate partition key."""
        return f"{entity_type}#{entity_id}"
    
    def is_fetched(self, entity_type: str, entity_id: str, date: str) -> bool:
        """Check if an entity has already been fetched for a given date."""
        pk = self._make_pk(entity_type, entity_id)
        response = self.table.get_item(
            Key={"pk": pk, "fetch_date": date}
        )
        item = response.get("Item")
        return item is not None and item.get("status") == "completed"
    
    def mark_fetched(self, entity_type: str, entity_id: str, date: str,
                     s3_key: str, record_count: int):
        """Record a completed fetch."""
        pk = self._make_pk(entity_type, entity_id)
        self.table.put_item(Item={
            "pk": pk,
            "fetch_date": date,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "s3_key": s3_key,
            "record_count": record_count,
            "status": "completed",
            "fetched_at": datetime.utcnow().isoformat()
        })
    
    def get_last_fetch_date(self, entity_type: str, entity_id: str) -> Optional[str]:
        """Get the most recent fetch date for an entity."""
        pk = self._make_pk(entity_type, entity_id)
        response = self.table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": pk},
            ScanIndexForward=False,  # Descending order
            Limit=1
        )
        items = response.get("Items", [])
        return items[0]["fetch_date"] if items else None
```

#### DynamoDB Table Creation (CloudFormation)

```yaml
Resources:
  FetchLogTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: nba-data-fetch-log
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: fetch_date
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: fetch_date
          KeyType: RANGE
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true
```

#### Pros & Cons

| Pros | Cons |
|------|------|
| Highly scalable | Additional AWS service to manage |
| Concurrent-safe | Small additional cost |
| Fast lookups | More complex setup |
| Built-in TTL for cleanup | Requires DynamoDB expertise |

---

### Option C: S3 Object Existence Check

Check if the target S3 object already exists before fetching.

#### Implementation

```python
# lib/helpers/fetch_tracker_s3_exists.py
import boto3
from botocore.exceptions import ClientError

def s3_key_exists(bucket: str, key: str) -> bool:
    """Check if an S3 object exists."""
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise

# Usage
def fetch_if_not_exists(team_id: str, date: str, bucket: str):
    """Fetch team games only if not already in S3."""
    s3_key = f"team-games/{date}/{team_id}.csv"
    
    if s3_key_exists(bucket, s3_key):
        print(f"Skipping {team_id} for {date} - already fetched")
        return None
    
    df = fetch_team_games(team_id=team_id, date=date)
    upload_to_s3(df, bucket, s3_key)
    return df
```

#### Pros & Cons

| Pros | Cons |
|------|------|
| Simplest implementation | No metadata about fetches |
| No additional storage | HEAD request per check |
| Self-documenting (data exists = fetched) | Can't distinguish empty result from not-fetched |

---

## Comparison Summary

### Hosting Options

| Criterion | Lambda | ECS Fargate | EC2 Spot | Local Cron |
|-----------|--------|-------------|----------|------------|
| **Setup Complexity** | Medium | High | High | Low |
| **Max Runtime** | 15 min | Unlimited | Unlimited | Unlimited |
| **Cost** | ~$1/mo | ~$4/mo | ~$0.50/mo | ~$2-8/mo |
| **Reliability** | Very High | Very High | Medium (interruptions) | Low-Medium |
| **Scaling** | Automatic | Automatic | Manual | None |
| **Cold Start** | 1-5 sec | 30-60 sec | 2-5 min | None |
| **Maintenance** | Low | Medium | High | Medium |
| **Best For** | Quick tasks <15min | Long-running tasks | Cost-sensitive batch | Development/testing |

### State Tracking Options

| Criterion | S3 Manifest | DynamoDB | S3 Existence |
|-----------|-------------|----------|--------------|
| **Complexity** | Low | Medium | Very Low |
| **Cost** | Free | ~$0.25/mo | Free |
| **Concurrency Safe** | No | Yes | Yes |
| **Metadata Support** | Yes | Yes | No |
| **Query Flexibility** | Low | High | None |
| **Best For** | Single-threaded jobs | Production systems | Simple workflows |

---

## Recommendations

### For Getting Started (MVP)

**Use AWS Lambda + S3 Manifest**

- Simplest to set up and cheapest to run
- Suitable for fetching players, teams, and daily game summaries
- Use S3 manifest for state tracking

```
EventBridge → Lambda → S3
                ↓
          S3 Manifest (state)
```

### For Production Scale

**Use ECS Fargate + DynamoDB**

- Handles long-running backfills without timeout concerns
- DynamoDB provides robust state tracking with concurrent access
- Better observability with CloudWatch integration

```
EventBridge → ECS Fargate → S3
                   ↓
              DynamoDB (state)
```

### For Maximum Cost Savings

**Use EC2 Spot Instances + S3 Existence Check**

- Lowest compute costs with spot pricing
- Simple existence check avoids overhead of state tracking service
- Requires handling of spot interruptions

```
EventBridge → Lambda (launcher) → EC2 Spot → S3
                                      ↓
                               S3 Existence Check
```

---

## Decisions

This section captures the architectural decisions for implementing the NBA Data CLI hosting and data management strategy.

### Decision 1: MVP — Local Hosting with Cron Jobs

For the initial MVP, the application will run locally using cron jobs for scheduling. This approach:

- **Minimizes complexity**: No cloud infrastructure setup required to start
- **Enables rapid iteration**: Easy to develop, debug, and test locally
- **Defers cloud costs**: No AWS charges until the system is proven

**Rationale**: Getting the core data fetching and storage logic working locally is the priority. Cloud deployment can follow once the data pipeline is stable.

### Decision 2: Data Store Module with Progressive Storage

A `data_store` module will be created to abstract data persistence:

- **Phase 1 — Local Files**: Data is written to local files in a `data/` directory (git-ignored)
- **Phase 2 — S3 Integration**: The module will be extended to write to S3, keeping the same interface

**Benefits**:
- Clean separation of concerns between fetching and storage
- Easy testing without cloud dependencies
- Smooth migration path to S3 when ready

**Implementation Notes**:
- Add `data/` to `.gitignore` to prevent local data files from being committed
- The module should support both local and S3 backends via configuration or environment variables

### Decision 3: Eventual Plan — Spot Instances with S3 Storage

The production deployment will use EC2 Spot Instances with S3 for data storage:

- **Containerization**: The Python application will be Dockerized for consistent deployment
- **Spot Instances**: Scheduled via EventBridge/Lambda launcher for cost efficiency
- **S3 Storage**: All fetched data persisted to S3 with date-partitioned structure

**Scheduling Approach**: Use EventBridge to trigger a Lambda function that launches a spot instance. The spot instance runs the containerized fetch job, uploads results to S3, and self-terminates.

### Decision 4: Fetch Tracking with Per-Module Timestamps

A tracking system will monitor when data was last fetched for each module, with different update frequencies:

#### Update Frequency Strategy

| Data Type | Update Frequency | Strategy |
|-----------|------------------|----------|
| **Teams** | Yearly | Fetch once per year, overwrite existing data |
| **Players** | Yearly | Fetch once per year, overwrite existing data |
| **Career Stats** | Weekly/Monthly | Overwrite with latest cumulative data |
| **Game Boxscores** | Daily (during season) | Append new games, never overwrite historical |
| **Player Game Logs** | Daily (during season) | Append new games, never overwrite historical |

#### Tracking File Format

A simple JSON or CSV file will track fetch metadata:

```json
{
  "modules": {
    "teams": {
      "last_fetched": "2024-01-15T06:00:00Z",
      "update_frequency": "yearly",
      "strategy": "overwrite"
    },
    "players": {
      "last_fetched": "2024-01-15T06:05:00Z",
      "update_frequency": "yearly",
      "strategy": "overwrite"
    },
    "career_stats": {
      "last_fetched": "2024-01-20T06:00:00Z",
      "update_frequency": "weekly",
      "strategy": "overwrite"
    },
    "game_boxscores": {
      "last_fetched": "2024-01-21T06:00:00Z",
      "last_game_date": "2024-01-20",
      "update_frequency": "daily",
      "strategy": "append"
    },
    "player_game_logs": {
      "last_fetched": "2024-01-21T06:00:00Z",
      "last_game_date": "2024-01-20",
      "update_frequency": "daily",
      "strategy": "append"
    }
  }
}
```

#### Fetch Tracker Implementation Plan

1. **Parse**: Load the tracking file at the start of each fetch operation
2. **Check**: Determine if a fetch is needed based on `last_fetched` and `update_frequency`
3. **Fetch**: If needed, fetch data using appropriate date ranges
   - For "append" strategies, use `last_game_date` to determine the start date for fetching
   - For "overwrite" strategies, fetch all data and replace existing files
4. **Update**: After successful fetch, update the tracking file with new timestamps

**Date Range Handling**:
- For daily append operations (boxscores, game logs), calculate the date range from `last_game_date + 1 day` to today
- For overwrite operations, fetch all available data regardless of previous fetches

---

## Implementation Roadmap

### Phase 1: Local MVP Setup (Week 1-2)

- [ ] Create `data/` directory and add to `.gitignore`
- [ ] Implement `data_store` module with local file backend
  - [ ] Create `lib/data_store/__init__.py`
  - [ ] Implement `save()` and `load()` functions for CSV data
  - [ ] Add configuration for output directory
- [ ] Create fetch tracking file (`data/fetch_tracker.json`)
  - [ ] Implement tracker parsing and update logic
  - [ ] Add `should_fetch()` helper based on update frequency
- [ ] Set up local cron job configuration
  - [ ] Create example crontab entries in `scripts/crontab.example`
  - [ ] Document cron setup in README or separate doc

### Phase 2: Fetch Tracker Integration (Week 3)

- [ ] Integrate fetch tracker with existing fetch commands
- [ ] Implement date range filtering for append strategies
  - [ ] Modify `fetch_player_games.py` to accept date range parameters
  - [ ] Modify `fetch_team_box_scores.py` to accept date range parameters
- [ ] Add deduplication logic to prevent redundant fetches
- [ ] Test idempotency of fetch operations

### Phase 3: S3 Integration (Week 4)

- [ ] Extend `data_store` module to support S3 backend
  - [ ] Add boto3 dependency to requirements.txt
  - [ ] Implement S3 save/load functions
  - [ ] Add backend selection via environment variable
- [ ] Configure S3 bucket structure as documented
- [ ] Set up IAM roles and bucket policies
- [ ] Set up lifecycle policies for cost management

### Phase 4: Containerization (Week 5)

- [ ] Create Dockerfile for the application
- [ ] Test container locally with docker-compose
- [ ] Document container build and run process
- [ ] Push container image to ECR (or Docker Hub for testing)

### Phase 5: Spot Instance Deployment (Week 6)

- [ ] Create EC2 launch template for spot instances
- [ ] Create Lambda function to launch spot instances
- [ ] Set up EventBridge schedules for automated execution
- [ ] Implement self-termination in spot instance user data script

### Phase 6: Production Hardening (Week 7-8)

- [ ] Add comprehensive logging
- [ ] Implement retry logic for transient failures
- [ ] Create runbook for common issues
- [ ] Set up cost monitoring and alerts

---

## Related Documentation

- [Scheduler Planning](scheduler.md) - Scheduling strategies and rate limiting
- [Data Model](data_model.md) - Entity schemas and relationships
- [README](../README.md) - CLI usage and project overview

---

## Revision History

| Date | Author | Description |
|------|--------|-------------|
| 2024-12-02 | Copilot | Initial hosting planning document |
| 2024-12-02 | Copilot | Added Decisions section and updated Implementation Roadmap |
