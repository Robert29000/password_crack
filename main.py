import argparse
from hashlib import sha384

from rainbow_table import RainbowTable
from utils import generate_data


def get_args():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="action")

    parser_gen = subparsers.add_parser('generate')

    parser_gen.add_argument('-l', '--len', type=int, required=True)
    parser_gen.add_argument('--cn', type=int, required=True)
    parser_gen.add_argument('--cl', type=int, required=True)
    parser_gen.add_argument('-i', '--input_alphabet', type=str)
    parser_gen.add_argument('-o', '--output_file', type=str)

    parser_crack = subparsers.add_parser('crack')

    parser_crack.add_argument('--input_table', type=str)
    parser_crack.add_argument('--input_hashes', type=str)

    return parser.parse_args()


def get_alphabet(input_file):
    with open(input_file, 'r') as input:
        return input.readline()


def main():
    args = get_args()

    if args.action == "generate":
        psw_length = args.len
        chains_num = args.cn
        chains_len = args.cl
        alphabet = get_alphabet(args.input_alphabet)
        output_dir = args.output_file

        table = RainbowTable(psw_length, alphabet, chains_num, chains_len, sha384)

        table.generate_table()
        table.save(output_dir)

    elif args.action == "crack":
        table = RainbowTable.load(args.input_table)

        # print(len(table.chains))
        # print(table.psw_len)
        # print(table.chains_num)
        # print(table.chains_len)

        # generate_data(table, 100, 'data/hashes.txt', 'data/answers.txt')

        found = 0

        hashes = None
        results = None

        with open(args.input_hashes, 'r') as data:
            hashes = data.read().splitlines()

            results = table.recover_words(hashes)

        for hash, res in zip(hashes, results):
            if res:
                found += 1
                print(hash, ' -> ', res)
            else:
                print(hash, ' -> ', 'Not found')

        print('Found - ', found)


if __name__ == '__main__':
    main()
