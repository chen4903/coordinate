import config
from main.Blockchain import *

# 1.编译合约
# BlockchainUtils.Compile("E:\coordinate\contracts\example.sol","a")

# 2.创建EOA账户
# BlockchainUtils.createEOA()

# 3.签名一个消息
#   没以太坊消息前缀（结果一致）
# c14e962f32ccedf712c80242275a65a6dc071592cfcbb6ac992170d2b865f8eb7b7c4aca2ac6e7060997abe82f3102b4a0017e725be310284406e9756223ff931c
# BlockchainUtils.signMessage("a",config.privateKey)
#   没以太坊消息前缀（结果随机）
# BlockchainUtils.randomSign("0000000000000000000000000000000000000000000000000000000000000001","f")

# 4.签名一个消息：有以太坊消息前缀
# 0x4118839afc359a4773981bbc4edbba36ad8aafe8f24282b5cde2f6490a4e33b63d478cd894428220180dd8998b138fec7634af90ec8ff0451257e646ef3aea231b
# chain=Chain(config.goerliAPI)
# account=Account(chain,config.privateKey)
# account.SignMessage("a")

# 5.将 R S V 合并成签名
# BlockchainUtils.RSVToSignature("0xc14e962f32ccedf712c80242275a65a6dc071592cfcbb6ac992170d2b865f8eb","0x7b7c4aca2ac6e7060997abe82f3102b4a0017e725be310284406e9756223ff93","0x1c")

# 6.将签名解析成 R S V
# BlockchainUtils.SignatureToRSV("0xc14e962f32ccedf712c80242275a65a6dc071592cfcbb6ac992170d2b865f8eb7b7c4aca2ac6e7060997abe82f3102b4a0017e725be310284406e9756223ff931c")

# 7.根据消息和签名恢复签署者的地址
# BlockchainUtils.RecoverMessage("a","0xc14e962f32ccedf712c80242275a65a6dc071592cfcbb6ac992170d2b865f8eb7b7c4aca2ac6e7060997abe82f3102b4a0017e725be310284406e9756223ff931c")

# 8.根据消息哈希和签名恢复签署者的地址
# BlockchainUtils.RecoverMessageHash("0x3ac225168df54212a25c1c01fd35bebfea408fdac2e31ddd6f80a4bbf9a5f1cb","0xc14e962f32ccedf712c80242275a65a6dc071592cfcbb6ac992170d2b865f8eb7b7c4aca2ac6e7060997abe82f3102b4a0017e725be310284406e9756223ff931c")

# 9.函数选择器碰撞
# BlockchainUtils.CrackSelector("hello",["string","uint256"],["uint256"])

# 10.获取某账户以 CREATE 方式部署的合约的地址
# BlockchainUtils.GetContractAddressByCREATE("0xd3E65149C212902749D49011B6ab24bba30D97c6",795)

# 11.Kecca256
# BlockchainUtils.Keccak256("hello")

# 12.根据私钥来获得公钥
# BlockchainUtils.GetPublicKeyFromPrivateKey(config.privateKey)

# 13.根据公钥获取地址
# BlockchainUtils.GetAddressFromPublicKey("0x57bffa5cd5803fb0f50dc86d9b1c51c08d9679a42fbc2e3f6c6d0f0d24150989103adbe5f8c032597501a8aa33837ea74dda3571cf4ced21eb9336308a98988d")

# 14.
# ether => wei
# BlockchainUtils.EtherToWei(1)

# wei => ether
# BlockchainUtils.WeiToEther(1000000000000000000)

# 15.获得包含特殊内容的地址，通过CREATE2
# BlockchainUtils.GetSpecialAddressByCreate2()
# BlockchainUtils.GetSpecialAddressByCreate2_two()

# 16.直接用calldata发送交易
# chain=Chain(config.goerliAPI)
# account=Account(chain,config.privateKey)
# account.SendTransaction()

# 17.发送以太币
# chain=Chain(config.goerliAPI)
# account=Account(chain,config.privateKey)
# account.Transfer()

# 18.获取slot
# chain=Chain(config.goerliAPI)
# chain.IterateStorage()
# chain.GetStorage()

# 19.获取函数选择器
# BlockchainUtils.GetFunctionSelector("setX",["uint256","uint256"])
# BlockchainUtils.GetFunctionSelector("getX",)

# 20.查询链ID
# chain=Chain("http://47.113.223.248:8545")
# print(chain.ChainId)