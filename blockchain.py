blockchain = []


def blockchain_value():
  return blockchain[-1]


def add_value(transaction_amount, last_transaction=[1]):
  blockchain.append([last_transaction, transaction_amount])


add_value(2)
add_value(.9, blockchain_value())
add_value(8.9, blockchain_value())


print(blockchain)