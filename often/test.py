import time
from web3 import Web3

import config
from main.Blockchain import Chain, BlockchainUtils,Account,Contract
from main.Math import Numbertheory

# chain = Chain("http://34.91.186.161:8545/wCpRGstyxSvhWiYsHEGuwxoe/main")
# print(chain.ChainId)

# print(Numbertheory.CRT([3, 5, 7],[2, 4, 3]))
# 207 / 10 = 20    7
# 207 / 5 = 41    2
# 207 / 30  = 6   27

# publickey = BlockchainUtils.GetPublicKeyFromPrivateKey("1647232166993cea928b43349a045c9cb703580480a3de10b7049cd320732c73")
# BlockchainUtils.GetAddressFromPublicKey(publickey)