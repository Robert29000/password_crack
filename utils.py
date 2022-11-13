def generate_data(table, num, hashes_filepath, answers_filepath):
    with open(answers_filepath, 'w') as answer:
        with open(hashes_filepath, 'w') as hashes:
            for _ in range(num):
                word = table.random_word()
                hash = table.hash_word(word)

                hashes.write(hash + '\n')
                answer.write(hash + ' -> ' + word + '\n')
