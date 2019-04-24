import json

def main():
	filename = '../twitter.json'
	with open(filename, encoding='utf8') as f:
		data = json.load(f)
		print(len(data))


if __name__ == "__main__":
	main()
