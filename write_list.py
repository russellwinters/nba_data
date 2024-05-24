import csv


class FileUtils:
    def read_csv_file(file_name):
        with open(file_name, 'r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)
            return list(first_row)

    def write_list_to_csv(file_name, data):
        with open(file_name, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(data)
