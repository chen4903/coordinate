import time
from web3 import Web3

import config
from main.Blockchain import Chain, BlockchainUtils,Account,Contract
from main.Math import Numbertheory

chain = Chain("https://bsc-testnet.blockpi.network/v1/rpc/public")
print(chain.ChainId)

# print(Numbertheory.CRT([3, 5, 7],[2, 4, 3]))
# 207 / 10 = 20    7
# 207 / 5 = 41    2
# 207 / 30  = 6   27