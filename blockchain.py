from functools import reduce
from collections import OrderedDict
from hash_util import hash_string_256, hash_block
from block import Block
from transaction import Transaction
import hashlib as hl
import json
import pickle


# Initialize
MINING_REWARD = 10

blockchain = []
open_transactions = []
owner = 'Nick'


def load_data():
    global blockchain
    global open_transactions

    try:
        with open('blockchain.txt', mode='r') as f:
            # use mode=r and file_name.txt for json/txt
            # use mode=rb and file_name.p for pickling

            # PICKLE #######
            # file_content = pickle.loads(f.read())
            ################

            file_content = f.readlines()

            print(file_content)

            # PICKLE ########
            # blockchain = file_content['chain']
            # open_transactions = file_content['ot']
            #################

            # converts json to python, and excludes \n which gets added in save_data, using [:-1]
            blockchain = json.loads(file_content[0][:-1])
            # updated_blockchain is used to put saved data, back into an OrderedDict
            # for when the file is saved, OrderedDict is stripped from the blockchain transaction data
            # but mined blocks already used it in the hashing algorithm
            # if it is not replaced, when a hash is recalculated, it will not match the previous_hash string
            updated_blockchain = []
            for block in blockchain:
                # helper variable
                converted_tx = [Transaction(
                    tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                # using the Block class to create a block
                updated_block = Block(
                    block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            # there is no new line after open_transactions, so we do not need [:-1]
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(
                    tx['sender'], tx['recipient'], tx['amount'])
                updated_transactions.append(updated_transaction)
                open_transactions = updated_transactions
    except (IOError, IndexError):
        genesis_block = Block(0, '', [], 100, 0)
        blockchain = [genesis_block]
        open_transactions = []
    finally:
        print('Cleanup!')


load_data()


# save blockchain data in external file
def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:
            # use mode=w, because we always want to overwrite blockchain, with new snapshot of data
            # use file_name.txt
            saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                                                                 tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in blockchain]]
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            saveable_tx = [tx.__dict__ for tx in open_transactions]
            f.write(json.dumps(saveable_tx))

            # to write to binary instead of default txt, you need mode=wb
            # you can save the file as file_name.p instead of file_name.txt
            # it isn't required but you can
            # save_data = {
            #     'chain': blockchain,
            #     'ot': open_transactions,

            # }
            # f.write(pickle.dumps(save_data))
    except IOError:
        print('Saving Failed')


def valid_proof(transactions, last_hash, proof):
    guess = (str([tx.to_ordered_dict() for tx in transactions]) +
             str(last_hash) + str(proof)).encode()
    print(guess, "GUESS GUESS GUES")
    guess_hash = hash_string_256(guess)
    print(guess_hash, "GUESS HASH")
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    # recalculating a previous block, storing it in last_hash
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


# Nested list comprehension
# GET an amount for a given transaction
# FOR all transactions in a block
# IF the sender is a participant
# You can read this forwards, starting from the smallest piece to the largest piece


def get_balance(participant):
    tx_sender = [[tx.amount for tx in block.transactions
                  if tx.sender == participant] for block in blockchain]
    open_tx_sender = [tx.amount
                      for tx in open_transactions if tx.sender == participant]
    tx_sender.append(open_tx_sender)
    print(tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                         if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx.amount for tx in block.transactions
                     if tx.recipient == participant] for block in blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    return amount_received - amount_sent


# check senders balance
def verify_transaction(transaction):
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount

# append previous and new value to blockchain
# arguments:
#   :sender: The sender of the coins
#   :recipient: The recipient of the coins.
#   :amount: The amount of coins sent with the transaction (default = 1.0)


def add_transaction(recipient, sender=owner, amount=[1.0]):
    #    transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
    # OrderedDict, creates an ordered dictionary so it's always the same, as dictionaries are
    # otherwise, unless altered, Normally unordered
    transaction = Transaction(sender, recipient, amount)
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


def mine_block():
  # a block should be a dictionary
  # previous hash -> summarized value of the previous block
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = Transaction('MINING', owner, MINING_REWARD)
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    print(hashed_block, 'HASHED BLOCK')
    block = Block(len(blockchain), hashed_block, copied_transactions, proof)
    blockchain.append(block)
    return True


# User input function
def get_transaction_value():
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))
    return (tx_recipient, tx_amount)


# User choice function
def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


# Blockchain print function
def print_blockchain_elements():
    # Output the blockchain list to the console
    for block in blockchain:
        print('Output blockchain')
        print(block)
    # executes once your done with a for loop
    else:
        print('-' * 20)


# Verify chain, runs after every selection is completed
# it compares every block in the current chain, with the previous block.
# it does not perform proof of work, that only happens when a block is mined.
# it uses the nonce however to make sure all the pow checkout, as is designed,
# so its easy to verify, but hard to solve.
def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        # if hash's are not the same, chain has been altered
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
            # we use [:-1] when validating,
            # to exclude the rewards from the validation process.
            # they are added to the transactions for the new block.
            # they were never included or used in the POW HASH for the last block
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print('Proof of work is invalid!')
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

while waiting_for_input:
    print('please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Check transaction validity')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data  # unpack/destructure tx_data tuple
        # add transaction amount to the blockchain
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions, 'OPEN TRANSACTIONS')
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('There are invalid transactions')
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        print(blockchain, 'BLOCKCHAIN')
        print(blockchain[0], 'BLOCKCHAIN 0')
        break
    print('Balance of {}: {:6.2f}'.format('Nick', get_balance('Nick')))

# executes once your done with a while loop
else:
    print('user left!')


print('Done')
