import csv
import tempfile
import os

input_file_path = '../dataset/nytcrosswords.csv'

with open(input_file_path, mode='r', newline='', encoding='latin-1') as infile, \
     tempfile.NamedTemporaryFile('w', delete=False, newline='', encoding='latin-1') as temp_file:
    
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['Length']
    writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
    
    writer.writeheader()
    for row in reader:
        row['Length'] = len(row['Word'])
        writer.writerow(row)

os.replace(temp_file.name, input_file_path)
