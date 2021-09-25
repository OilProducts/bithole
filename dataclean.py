import csv

data = []
with open('puzzle_transactions_dirty.csv', 'r') as puzzle_dirty:
    reader = csv.DictReader(puzzle_dirty)
    for item in reader:
        data.append(item)

print(data)
with open('puzzle_transactions.csv', 'w') as puzzle_clean:
    writer = csv.DictWriter(puzzle_clean, list(data[0].keys()))
    writer.writeheader()

    for item in data:
        start_int = item['start_int']
        item['start_int'] = 2 ** int(start_int[1:])

        stop_int = item['stop_int']
        item['stop_int'] = (2 ** int(stop_int[1:])) - 1

        start_hex = item['start_hex']
        item['start_hex'] = start_hex.strip()

        stop_hex = item['stop_hex']
        item['stop_hex'] = stop_hex.strip()

        private_key = item['private_key']
        item['private_key'] = private_key.strip()

        address = item['address']
        addr_pots = bytes(address, encoding='utf-8').split(b'\xc2\xa0')
        item['address'] = str(addr_pots[1])[2:-1]

        writer.writerow(item)