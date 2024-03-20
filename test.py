base_url = "https://huggingface.co/datasets/osbm/camelyon16/resolve/main/data/images/"
format_string = "tumor_{:03d}.tif"

for i in range(1, 112):
    link = base_url + format_string.format(i)
    print(link)