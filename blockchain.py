blockchain = []


def blockchain_value():
  return blockchain[-1]


def add_value(transaction_amount, last_transaction=[1]):
  blockchain.append([last_transaction, transaction_amount])

def get_user_input():
  return float(input('Your transaction amount please > '))


#I can wrap input with float, and the string won't cause an issue, while it handles the input
tx_amount = get_user_input()
add_value(tx_amount)

tx_amount = get_user_input()
add_value(last_transaction=blockchain_value(), transaction_amount=tx_amount)

tx_amount = get_user_input()
add_value(tx_amount, blockchain_value())


print(blockchain)