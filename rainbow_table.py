import random
import pickle
from itertools import repeat
from multiprocessing import Pool, Manager, Value
from tqdm import tqdm


class RainbowTable:

    def __init__(self, psw_len, alphabet, chains_num, chains_len, hash_func):
        self.psw_len = psw_len
        self.alphabet = alphabet
        self.chains_num = chains_num
        self.chains_len = chains_len
        self.hash_func = hash_func

        self.chains = {}

    def generate_table(self):
        chains = Manager().dict()

        with Pool() as pool:
            # pool.map(self.generate_chain, repeat(chains, self.chains_num))

            for _ in tqdm(pool.imap_unordered(self.generate_chain_without_dup, repeat(chains, self.chains_num)),
                          total=self.chains_num):
                pass
            # p_map(self.generate_chain, repeat(chains, self.chains_num))

        self.chains = dict(chains)

    def generate_chain(self, chains):
        start_word = self.random_word()

        word = start_word
        hash = None

        for step in range(self.chains_len):
            hash = self.hash_word(word)
            word = self.reduce_hash(hash, step)

        chains[hash] = start_word

    def generate_chain_without_dup(self, chains):
        while True:
            start_word = self.random_word()

            word = start_word
            hash = None

            for step in range(self.chains_len):
                hash = self.hash_word(word)
                word = self.reduce_hash(hash, step)

            if hash not in chains:
                chains[hash] = start_word
                break

    def recover_words(self, hashes):
        results = []

        with Pool() as pool:
            for res in tqdm(pool.imap(self.recover_word, hashes), total=len(hashes)):
                results.append(res)

        return results

    def recover_word(self, hash):
        for step in range(self.chains_len - 1, -1, -1):
            hash_final = self.hash_with_step(hash, step)

            if hash_final in self.chains:
                word = self.chains[hash_final]
                res = self.find_in_chain(word, hash)

                if res:
                    return res

        return None

    def random_word(self):
        return "".join(random.choices(self.alphabet, k=self.psw_len))

    def hash_with_step(self, hash_start, step_start):
        hash = hash_start

        for step in range(step_start, self.chains_len - 1):
            word = self.reduce_hash(hash, step)
            hash = self.hash_word(word)

        return hash

    def find_in_chain(self, word, hash_check):
        hash = self.hash_word(word)
        if hash == hash_check:
            return word

        for step in range(self.chains_len):
            word = self.reduce_hash(hash, step)
            hash = self.hash_word(word)

            if hash == hash_check:
                return word

        return None

    def hash_word(self, word):
        word = word.encode("utf-8")
        return self.hash_func(word).hexdigest()

    def reduce_hash(self, hash_str, step):
        res = ""

        for i in range(self.psw_len):
            init_val = (i + step) % (len(hash_str) - 1)  # maybe add random

            idx = int(hash_str[init_val: init_val + 2],
                      16)  # generate index based on byte value from hash and chain step
            res += self.alphabet[(idx ^ step) % len(self.alphabet)]

        return res

    @property
    def collisions(self):
        num = self.chains_num - len(self.chains)
        percent = (self.chains_num - len(self.chains)) / self.chains_num
        return num, percent

    def save(self, filepath):
        with open(filepath, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    # def load(self, filepath):  # test work
    #     with open(filepath, 'rb') as input:
    #         tmp_table = pickle.load(input)
    #         self.__dict__.update(tmp_table.__dict__)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as input:
            return pickle.load(input)
