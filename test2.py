import csv

base_url = "https://huggingface.co/datasets/osbm/camelyon16/resolve/main/data/images/"
normal_format_string = "normal_{:03d}"
tumor_format_string = "tumor_{:03d}"

with open('output.csv', 'w', newline='') as csvfile:
    fieldnames = ['case_id', 'slide_id', 'label']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    # Writing normal cases
    for i in range(1, 161):
        case_id = f"patient_{i}"
        slide_id = normal_format_string.format(i)
        label = "normal_tissue"
        writer.writerow({'case_id': case_id, 'slide_id': slide_id, 'label': label})
    
    # Writing tumor cases
    for i in range(1, 112):  # Adjusted the range to 1 to 111
        case_id = f"patient_{i+160}"  # Adjusted the index offset to 160
        slide_id = tumor_format_string.format(i)
        label = "tumor_tissue"
        writer.writerow({'case_id': case_id, 'slide_id': slide_id, 'label': label})
