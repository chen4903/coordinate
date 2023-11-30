import os
from web3 import Web3, utils
from eth_account import Account as EthAccount
from loguru import logger
from typing import Optional, Union, List, Any
from traceback import format_exc
from json import dump, dumps
from eth_utils import keccak
from coincurve import PublicKey
from binascii import unhexlify,hexlify
import time
import random
from ecdsa import ecdsa
import execjs

class Chain():
    """
    Chain 是区块链实例，用于读取链上数据
    """

    def __init__(self, RPCUrl: str):
        """
        初始化。根据给定的节点 RPC 地址以 HTTP/HTTPS 方式进行连接，

        参数：
            RPCUrl (str): 节点 RPC 地址

        成员变量：
            ChainId (int): 链 ID
            Node (Web3.HTTPProvider): web3.py 原生的 HTTP 交互器实例
            Eth (Web3.HTTPProvider.eth): HTTP 交互器实例中的 eth 模块
        """

        from web3 import HTTPProvider
        from web3.middleware import geth_poa_middleware
        self.Node = Web3(HTTPProvider(RPCUrl))
        if self.Node.is_connected():
            logger.success(f"\n[Chain][Initialize] Connected to [{RPCUrl}]\n{'-'*100}")
            self.Node.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.Eth = self.Node.eth
            self.ChainId, BlockNumber, GasPrice = self.Eth.chain_id, self.Eth.block_number, self.Eth.gas_price
        else:
            logger.error(f"\n[Chain][Initialize] Failed to connect to [{RPCUrl}]\n{'-'*100}")
            raise Exception("Failed to connect to chain.")


    def GetBasicInformation(self) -> dict:
        """
        获取区块链基本信息。包括 ChainId 、BlockNumber 、GasPrice 、(Timeslot)、ClientVersion 。

        参数：
            ShowTimeslot (bool): 是否获取并显示 Timeslot 。该操作比较耗时，在主动调用时默认为 True , 在 Chain 实例初始化时默认为 False 。

        返回值：
            BasicInformation (dict): 区块链基本信息构成的字典。
            {"ChainId"|"BlockNumber"|"GasPrice"|("Timeslot")|"ClientVersion"}
        """

        self.ChainId, BlockNumber, GasPrice= self.Eth.chain_id, self.Eth.block_number, self.Eth.gas_price
        logger.success(
            f"\n[Chain][GetBasicInformation]\n[ChainId] {self.ChainId}\n[BlockNumber] {BlockNumber}\n[GasPrice] {Web3.from_wei(GasPrice, 'gwei')} Gwei\n{'-'*80}"
        )
        BasicInformation = {
            "ChainId": self.ChainId,
            "BlockNumber": BlockNumber,
            "GasPrice": GasPrice,
        }
        return BasicInformation

    def GetTransactionInformationByHash(self, TransactionHash: str) -> dict:
        """
        根据交易哈希查询该交易的详细回执信息。包括交易哈希、所在区块号、交易索引号、交易状态、交易类型、交易行为、发送者、接收者、(部署的合约地址)、(GasPrice 或 (MaxFeePerGas 和 MaxPriorityFeePerGas))、GasLimit、GasUsed、Nonce、Value、R、S、V、Logs、InputData。

        参数：
            TransactionHash (str): 要查询的交易的哈希

        返回值：
            TransactionInformation (dict): 交易信息构成的字典。当出现异常时返回 None 。
            {"TransactionHash"|"BlockNumber"|"TransactionIndex"|"Status"|"Type"|"Action"|"From"|"To"|("ContractAddress")|<"GasPrice"|("MaxFeePerGas"&"MaxPriorityFeePerGas")>|"GasLimit"|"GasUsed"|"Nonce"|"Value"|"R"|"S"|"V"|"Logs"|"InputData"}
        """

        try:
            # 在这段代码中，可能之所以定义了两次 Info 变量，是因为需要通过不同的方法来获取交易的不同信息。第一次定义的 Info 通过等待交易收据的方式获取了一些信息，
            # 而第二次定义的 Info 则通过直接获取交易的方式获取了其他信息。这样做可能是为了方便后续操作，将获取到的信息分别存储在不同的变量中以供使用。
            Info = self.Eth.wait_for_transaction_receipt(TransactionHash, timeout=120)
            BlockNumber, TransactionIndex, Status, From, To, ContractAddress, GasUsed, Logs = Info.blockNumber, Info.transactionIndex, Info.status, Info["from"], Info.to, Info.contractAddress, Info.gasUsed, Web3.to_json(Info.logs)
            Info = self.Eth.get_transaction(TransactionHash)
            TransactionHash, GasPrice, MaxFeePerGas, MaxPriorityFeePerGas, GasLimit, Nonce, Value, R, S, V, InputData = Info.hash.hex(), Info.gasPrice, Info.get("maxFeePerGas", None), Info.get("maxPriorityFeePerGas", None), Info.gas, Info.nonce, Info.value, Info.r.hex(), Info.s.hex(), Info.v, Info.input

            Type = "EIP-1559" if MaxFeePerGas or MaxPriorityFeePerGas else "Traditional"
            Action = "Deploy Contract" if To == None else "Call Contract" if self.Eth.get_code(Web3.to_checksum_address(To)).hex() != "0x" else "Normal Transfer"
            ContractPrint = f"[ContractAddress] {ContractAddress}\n" if ContractAddress else ""
            GasPricePrint = f"[MaxFeePerGas] {Web3.from_wei(MaxFeePerGas, 'gwei')} Gwei\n[MaxPriorityFeePerGas] {Web3.from_wei(MaxPriorityFeePerGas, 'gwei')} Gwei" if Type == "EIP-1559" else f"[GasPrice] {Web3.from_wei(GasPrice, 'gwei')} Gwei"
            GeneralPrint = f"\n[Chain][GetTransactionInformationByHash]\n[TransactionHash] {TransactionHash}\n[BlockNumber] {BlockNumber}\n[TransactionIndex] {TransactionIndex}\n[Status] {'Success' if Status else 'Fail'}\n[Type] {Type}\n[Action] {Action}\n[From] {From}\n[To] {To}\n{ContractPrint}{GasPricePrint}\n[GasLimit] {GasLimit}\n[GasUsed] {GasUsed}\n[Nonce] {Nonce}\n[Value] {Value}\n[R] {R}\n[S] {S}\n[V] {V}\n[Logs] {Logs}\n[InputData] {InputData}\n{'-'*80}"
            if Status:
                logger.success(GeneralPrint)
            else:
                logger.error(GeneralPrint)
            TransactionInformation = {
                "TransactionHash": TransactionHash,
                "BlockNumber": BlockNumber,
                "TransactionIndex": TransactionIndex,
                "Status": Status,
                "Type": Type,
                "Action": Action,
                "From": From,
                "To": To,
                "ContractAddress": ContractAddress,
                "GasPrice": GasPrice,
                "MaxFeePerGas": MaxFeePerGas,
                "MaxPriorityFeePerGas": MaxPriorityFeePerGas,
                "GasLimit": GasLimit,
                "GasUsed": GasUsed,
                "Nonce": Nonce,
                "Value": Value,
                "R": R,
                "S": S,
                "V": V,
                "Logs": Logs,
                "InputData": InputData
            }
            return TransactionInformation
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Chain][GetTransactionInformationByHash]Failed\n[TransactionHash]{TransactionHash}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def GetTransactionInformationByBlockIdAndIndex(self, BlockID: Union[str, int], TransactionIndex: int) -> dict:
        """
        根据区块 ID 和交易在块中的索引来查询该交易的详细回执信息。包括交易哈希、所在区块号、交易索引号、交易状态、交易类型、交易行为、发送者、接收者、(部署的合约地址)、(GasPrice 或 (MaxFeePerGas 和 MaxPriorityFeePerGas))、GasLimit、GasUsed、Nonce、Value、R、S、V、Logs、InputData。

        参数：
            BlockID (Union[str,int]): 区块 ID 。可为区块号数值或 'latest', 'earliest', 'pending' 。
            TransactionIndex (int): 交易在块中的索引

        返回值：
            TransactionInformation (dict): 交易信息构成的字典。当出现异常时返回 None 。
            {"TransactionHash"|"BlockNumber"|"TransactionIndex"|"Status"|"Type"|"Action"|"From"|"To"|("ContractAddress")|<"GasPrice"|("MaxFeePerGas"&"MaxPriorityFeePerGas")>|"GasLimit"|"GasUsed"|"Nonce"|"Value"|"R"|"S"|"V"|"Logs"|"InputData"}
        """

        try:
            Info = self.Eth.get_transaction_by_block(BlockID, TransactionIndex)
            TransactionHash, BlockNumber, TransactionIndex, From, To, GasPrice, MaxFeePerGas, MaxPriorityFeePerGas, GasLimit, Nonce, Value, R, S, V, InputData = Info.hash.hex(), Info.blockNumber, Info.transactionIndex, Info["from"], Info.to, Info.gasPrice, Info.get("maxFeePerGas", None), Info.get("maxPriorityFeePerGas", None), Info.gas, Info.nonce, Info.value, Info.r.hex(), Info.s.hex(), Info.v, Info.input
            Info = self.Eth.wait_for_transaction_receipt(TransactionHash, timeout=120)
            Status, GasUsed, ContractAddress, Logs = Info.status, Info.gasUsed, Info.contractAddress, Info.logs
            Type = "EIP-1559" if MaxFeePerGas else "Traditional"
            Action = "Deploy Contract" if To == None else "Call Contract" if self.Eth.get_code(Web3.toChecksumAddress(To)).hex() != "0x" else "Normal Transfer"
            ContractPrint = f"[ContractAddress]{ContractAddress}\n" if ContractAddress else ""
            GasPricePrint = f"[MaxFeePerGas]{Web3.from_wei(MaxFeePerGas, 'gwei')} Gwei\n[MaxPriorityFeePerGas]{Web3.from_wei(MaxPriorityFeePerGas, 'gwei')} Gwei" if Type == "EIP-1559" else f"[GasPrice]{Web3.from_wei(GasPrice, 'gwei')} Gwei"
            GeneralPrint = f"\n[Chain][GetTransactionInformationByBlockIdAndIndex]\n[TransactionHash]{TransactionHash}\n[BlockNumber]{BlockNumber}\n[TransactionIndex]{TransactionIndex}\n[Status]{'Success' if Status else 'Fail'}\n[Type]{Type}\n[Action]{Action}\n[From]{From}\n[To]{To}\n{ContractPrint}{GasPricePrint}\n[GasLimit]{GasLimit} [GasUsed]{GasUsed}\n[Nonce]{Nonce} [Value]{Value}\n[R]{R}\n[S]{S}\n[V]{V}\n[Logs]{Logs}\n[InputData]{InputData}\n{'-'*80}"
            if Status:
                logger.success(GeneralPrint)
            else:
                logger.error(GeneralPrint)
            TransactionInformation = {
                "TransactionHash": TransactionHash,
                "BlockNumber": BlockNumber,
                "TransactionIndex": TransactionIndex,
                "Status": Status,
                "Type": Type,
                "Action": Action,
                "From": From,
                "To": To,
                "ContractAddress": ContractAddress,
                "GasPrice": GasPrice,
                "MaxFeePerGas": MaxFeePerGas,
                "MaxPriorityFeePerGas": MaxPriorityFeePerGas,
                "GasLimit": GasLimit,
                "GasUsed": GasUsed,
                "Nonce": Nonce,
                "Value": Value,
                "R": R,
                "S": S,
                "V": V,
                "Logs": Logs,
                "InputData": InputData
            }
            return TransactionInformation
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Chain][GetTransactionInformationByBlockIdAndIndex]Failed\n[BlockID]{BlockID}\n[TransactionIndex]{TransactionIndex}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def GetBlockInformation(self, BlockID: Union[str, int]) -> dict:
        """
        根据区块 ID 获取该区块的详细信息。包括区块号、区块哈希、矿工、时间戳、GasLimit、GasUsed、块内交易的哈希集合。

        参数：
            BlockID (Union[str,int]): 区块 ID 。可为区块号数值或 'latest', 'earliest', 'pending' 。

        返回值：
            BlockInformation (dict): 区块信息构成的字典。当出现异常时返回 None 。
            {"BlockNumber"|"BlockHash"|"Miner"|"TimeStamp"|"GasLimit"|"GasUsed"|"Transactions"}
        """

        try:
            Info = self.Eth.get_block(BlockID)
            BlockNumber, BlockHash, Miner, TimeStamp, GasLimit, GasUsed, Transactions = Info.number, Info.hash.hex(), Info.miner, Info.timestamp, Info.gasLimit, Info.gasUsed, Web3.to_json(Info.transactions)
            logger.success(
                f"\n[Chain][GetBlockInformation]\n[BlockNumber]{BlockNumber}\n[BlockHash]{BlockHash}\n[Miner]{Miner}\n[TimeStamp]{TimeStamp}\n[GasLimit]{GasLimit}\n[GasUsed]{GasUsed}\n[Transactions]{Transactions}"
            )
            BlockInformation = {
                "BlockNumber": BlockNumber,
                "BlockHash": BlockHash,
                "Miner": Miner,
                "TimeStamp": TimeStamp,
                "GasLimit": GasLimit,
                "GasUsed": GasUsed,
                "Transactions": Transactions
            }
            return BlockInformation
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Chain][GetBlockInformation]Failed\n[BlockID]{BlockID}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def GetBalance(self, Address: str) -> int:
        """
        根据账户地址获取其网络原生代币余额。

        参数：
            Address (str): 账户地址

        返回值：
            Balance (int): 账户网络原生代币余额，单位为 wei 。当出现异常时返回 None 。
        """

        try:
            Address = Web3.to_checksum_address(Address)
            Balance = self.Eth.get_balance(Address)
            logger.success(
                f"\n[Chain][GetBalance]\n[Address] {Address}\n[Balance] [{Balance} Wei <=> {Web3.from_wei(Balance,'ether')} Ether]\n{'-'*80}"
            )
            return Balance
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(f"\n[Chain][GetBalance]Failed\n[Address]{Address}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}")
            return None

    def GetBytecode(self, Address: str) -> str:
        """
        根据合约地址获取其已部署字节码。

        参数：
            Address (str): 合约地址

        返回值：
            Code (str): 合约已部署字节码。当出现异常时返回 None 。
        """

        try:
            Address = Web3.to_checksum_address(Address)
            Code = self.Eth.get_code(Address).hex()
            logger.success(f"\n[Chain][GetBytecode]\n[Address] {Address}\n[Bytecode] {Code}\n{'-'*80}")
            return Code
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(f"\n[Chain][GetBytecode]Failed\n[Address]{Address}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}")
            return None

    def GetStorage(self, Address: str, SlotIndex: int) -> str:
        """
        根据合约地址和存储插槽索引获取存储值。

        参数：
            Address (str): 合约地址
            SlotIndex (int): 存储插槽索引

        返回值：
            Data (str): 存储值。当出现异常时返回 None 。
        """

        try:
            Address = Web3.to_checksum_address(Address)
            Data = self.Eth.get_storage_at(Address, SlotIndex).hex()
            logger.success(
                f"\n[Chain][GetStorage]\n[Address] {Address}\n[SlotIndex] {SlotIndex}\n[Value]  [Hex][{Data}] <=> [Dec][{int(Data,16)}]\n{'-'*80}"
            )
            return Data
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Chain][GetStorage]Failed\n[Address]{Address}\n[SlotIndex]{SlotIndex}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def IterateStorage(self, Address: str, Count: int) -> list:
        """
        根据合约地址和指定插槽数量值，从插槽 0 开始批量遍历存储插槽并获取值。

        参数：
            Address (str): 合约地址
            Count (int): 指定插槽数量值

        返回值：
            Data (List[str]): 存储值列表。当出现异常时返回 None 。
        """

        try:
            Address = Web3.to_checksum_address(Address)
            Data = [self.Eth.get_storage_at(Address, i).hex() for i in range(Count)]
            Temp = '\n'.join([f"[Slot {i}] {Data[i]}" for i in range(len(Data))])
            logger.success(f"\n[Chain][IterateStorage]\n[Address] {Address}\n{Temp}\n{'-'*80}")
            return Data
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Chain][DumpStorage]Failed\n[Address]{Address}\n[slot 0 ... {Count-1}]\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def GetPublicKeyByTransactionHash(self, TransactionHash: str) -> tuple:
        """
        通过一笔已在链上确认的交易哈希，获取账户公钥。

        参数：
            TransactionHash (str): 交易哈希

        返回值：
            (Address, PublicKey) (tuple): 由账户地址和账户公钥组成的元组。当出现异常时返回 None 。
        """

        try:
            from eth_account._utils.signing import to_standard_v, extract_chain_id, serializable_unsigned_transaction_from_dict

            Transaction = self.Eth.get_transaction(TransactionHash)
            Signature = self.Eth.account._keys.Signature(vrs=(to_standard_v(extract_chain_id(Transaction.v)[1]), Web3.to_int(Transaction.r), Web3.to_int(Transaction.s)))
            UnsignedTransactionDict = {i: Transaction[i] for i in ['chainId', 'nonce', 'gasPrice' if Transaction.type != 2 else '', 'gas', 'to', 'value', 'accessList', 'maxFeePerGas', 'maxPriorityFeePerGas'] if i in Transaction}
            UnsignedTransactionDict['data'] = Transaction['input']
            UnsignedTransaction = serializable_unsigned_transaction_from_dict(UnsignedTransactionDict)
            Temp = Signature.recover_public_key_from_msg_hash(UnsignedTransaction.hash())
            #PublicKey = str(Temp).replace('0x', '0x04')  # 比特币未压缩公钥格式
            PublicKey = str(Temp)
            Address = Temp.to_checksum_address()
            logger.success(
                f"\n[Chain][GetPublicKeyByTransactionHash]\n[TransactionHash] {TransactionHash}\n[Address] {Address}\n[PublicKey] {PublicKey}\n{'-'*80}"
            )
            return (Address, PublicKey)
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Chain][GetPublicKeyByTransactionHash]Failed\n[TransactionHash]{TransactionHash}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

class Account():
    """
    Account 是账户实例，后续的交易将经由该指定账户发送至链上。
    """

    def GetEOANonce(self):
        """
        获取当前账户的 Nonce值
        """
        print(self._Chain.Node.eth.get_transaction_count(self.EthAccount.address))

    def __init__(self, Chain: Chain, PrivateKey: str):
        """
        初始化。通过私钥导入账户并与 Chain 实例绑定，后续的交易将经由该指定账户发送至链上。当导入账户失败时将会抛出异常。

        参数：
            Chain (Poseidon.Blockchain.Chain): 区块链实例
            PrivateKey (str): 账户私钥。

        成员变量：
            EthAccount (eth_account.Account): eth_account 的原生 Account 对象实例
        """

        try:
            self.EthAccount, self._Chain, self._Eth = EthAccount.from_key(PrivateKey), Chain, Chain.Eth
            self._Eth.default_account = self.EthAccount.address
            logger.success(f"\n[Account][Initialize]Successfully import account [{self.EthAccount.address}]\n{'-'*80}")
            self.RequestAuthorizationBeforeSendTransaction(True)
            self.GetSelfBalance()
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(f"\n[Account][Initialize]Failed to import account\n[ExceptionInformation]{ExceptionInformation}{'-'*80}")
            raise Exception("Failed to import account.")

    def RequestAuthorizationBeforeSendTransaction(self, Open: bool = True):
        """
        设置在通过该账户发送每一笔交易之前是否请求授权。开启后会在每笔交易即将发送前暂停流程，在终端询问是否发送该笔交易。

        参数：
            Open (bool): 请求授权开关。主动调用时默认值为 True ，但在 Account 实例初始化时默认设置为 False 。
        """

        self._Request = Open
        if self._Request:
            logger.success(f"\n[Account][RequestAuthorizationBeforeSendTransaction]Open: True\n{'-'*80}")
        else:
            logger.warning(f"\n[Account][RequestAuthorizationBeforeSendTransaction]Open: False\n{'-'*80}")

    def GetSelfBalance(self) -> int:
        """
        获取自身账户的网络原生代币余额。

        返回值：
            Balance (int): 自身账户网络原生代币余额，单位为 wei 。当出现异常时返回 None 。
        """

        Balance = self._Chain.GetBalance(self.EthAccount.address)
        if Balance == 0:
            logger.warning(f"\n[Account][GetSelfBalance]\n[Warning]This account's balance is insufficient to send transactions\n{'-'*80}")
        return Balance

    def Transfer(self, To: str, Value: int, Data: str = "0x", GasPrice: Optional[int] = None, GasLimit: int = 100000) -> dict:
        """
        向指定账户转账指定数量的网络原生代币，可附带信息。若 120 秒内交易未确认则作超时处理。

        参数：
            To (str): 接收方地址
            Value (int): 发送的网络原生代币数量，单位为 wei 。
            Data (可选)(str): 交易数据。含 0x 前缀的十六进制形式。默认值为 "0x" 。
            GasPrice (可选)(Optional[int]): Gas 价格，单位为 wei ，默认使用 RPC 建议的 gas_price 。
            GasLimit (可选)(int): Gas 最大使用量，单位为 wei ，默认为 100000 wei 。

        返回值：
            TransactionInformation (dict): 交易信息构成的字典，通过 Chain.GetTransactionInformationByHash 获取。当出现异常时返回 None 。
        """

        try:
            From = self.EthAccount.address
            To = Web3.to_checksum_address(To)
            Txn = {
                "chainId": self._Chain.ChainId,
                "from": From,
                "to": To,
                "value": Value,
                "gas": GasLimit,
                "gasPrice": GasPrice if GasPrice else self._Eth.gas_price,
                "nonce": self._Eth.get_transaction_count(From),
                "data": Data,
            }
            SignedTxn = self.EthAccount.sign_transaction(Txn)
            Txn["gasPrice"] = f'{Web3.from_wei(Txn["gasPrice"],"gwei")} Gwei'
            logger.info(f"\n[Account][Transfer]\n[Txn]{dumps(Txn, indent=2)}\n{'-'*80}")
            if self._Request:
                logger.warning(f"\n[Account][RequestAuthorizationBeforeSendTransaction][True]\nDo you confirm sending this transaction?")
                Command = input("Command Input (yes/1/[Enter] or no/0):")
                if Command == "no" or Command == "0" or (len(Command) > 0 and Command != "yes" and Command != "1"):
                    raise Exception("Cancel sending transaction.")
            print("pending...")
            TransactionHash = self._Eth.send_raw_transaction(SignedTxn.rawTransaction).hex()
            TransactionInformation = self._Chain.GetTransactionInformationByHash(TransactionHash)
            return TransactionInformation
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Account][Transfer]Failed\n[From]{From}\n[To]{To}\n[Value]{Value}\n[GasPrice]{GasPrice}\n[GasLimit]{GasLimit}\n[Data]{Data}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def SendTransaction(self, To: str, Data: str, Value: int = 0, GasPrice: Optional[int] = None, GasLimit: int = 1000000) -> dict:
        """
        以传统方式发送一笔自定义交易。若 120 秒内交易未确认则作超时处理。

        参数：
            To (str): 接收方地址
            Data (str): 交易数据。含 0x 前缀的十六进制形式。
            Value (可选)(int): 随交易发送的网络原生代币数量，单位为 wei ，默认为 0 wei 。
            GasPrice (可选)(Optional[int]): Gas 价格，单位为 wei ，默认使用 RPC 建议的 gas_price 。
            GasLimit (可选)(int): Gas 最大使用量，单位为 wei ，默认为 1000000 wei 。

        返回值：
            TransactionInformation (dict): 交易信息构成的字典，通过 Chain.GetTransactionInformationByHash 获取。当出现异常时返回 None 。
        """

        try:
            From = self.EthAccount.address
            To = Web3.to_checksum_address(To)
            Txn = {
                "chainId": self._Chain.ChainId,
                "from": From,
                "to": To,
                "value": Value,
                "gas": GasLimit,
                "gasPrice": GasPrice if GasPrice else self._Eth.gas_price,
                "nonce": self._Eth.get_transaction_count(From),
                "data": Data,
            }
            SignedTxn = self.EthAccount.sign_transaction(Txn)
            Txn["gasPrice"] = f'{Web3.from_wei(Txn["gasPrice"],"gwei")} Gwei'
            logger.info(f"\n[Account][SendTransaction][Traditional]\n[Txn]{dumps(Txn, indent=2)}\n{'-'*80}")
            if self._Request:
                logger.warning(f"\n[Account][RequestAuthorizationBeforeSendTransaction][True]\nDo you confirm sending this transaction?")
                Command = input("Command Input (yes/1/[Enter] or no/0):")
                if Command == "no" or Command == "0" or (len(Command) > 0 and Command != "yes" and Command != "1"):
                    raise Exception("Cancel sending transaction.")
            print("pending...")
            TransactionHash = self._Eth.send_raw_transaction(SignedTxn.rawTransaction).hex()
            TransactionInformation = self._Chain.GetTransactionInformationByHash(TransactionHash)
            return TransactionInformation
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Account][SendTransaction][Traditional]Failed\n[From]{From}\n[To]{To}\n[Value]{Value}\n[GasPrice]{GasPrice}\n[GasLimit]{GasLimit}\n[Data]{Data}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def SendTransactionByEIP1559(self, To: str, Data: str, Value: int = 0, BaseFee: Optional[int] = None, MaxPriorityFee: Optional[int] = None, GasLimit: int = 1000000) -> dict:
        """
        以 EIP-1559 方式发送一笔自定义交易。若 120 秒内交易未确认则作超时处理。
        比如：To是一个合约地址，构造 Data(也就是calldata),指定调用的方法。calldata: 函数选择器 + 参数，请注意 ABI 编码规则
        注意：此方法无法获取合约函数的返回值，只能发送交易和获取交易的信息

        参数：
            To (str): 接收方地址
            Data (str): 交易数据。含 0x 前缀的十六进制形式。
            Value (可选)(int): 随交易发送的网络原生代币数量，单位为 wei ，默认为 0 wei 。
            BaseFee (可选)(Optional[int]): BaseFee 价格，单位为 wei ，默认使用 RPC 建议的 gas_price 。
            MaxPriorityFee (可选)(Optional[int]): MaxPriorityFee 价格，单位为 wei ，默认使用 RPC 建议的 max_priority_fee 。
            GasLimit (可选)(int): Gas 最大使用量，单位为 wei ，默认为 1000000 wei 。

        返回值：
            TransactionInformation (dict): 交易信息构成的字典，通过 Chain.GetTransactionInformationByHash 获取。当出现异常时返回 None 。
        """

        try:
            From = self.EthAccount.address
            To = Web3.to_checksum_address(To)
            BaseFee = BaseFee if BaseFee else self._Eth.gas_price
            MaxPriorityFee = MaxPriorityFee if MaxPriorityFee else self._Eth.max_priority_fee
            Txn = {
                "chainId": self._Chain.ChainId,
                "from": From,
                "to": To,
                "value": Value,
                "gas": GasLimit,
                "maxFeePerGas": BaseFee + MaxPriorityFee,
                "maxPriorityFeePerGas": MaxPriorityFee,
                "nonce": self._Eth.get_transaction_count(From),
                "data": Data
            }
            SignedTxn = self.EthAccount.sign_transaction(Txn)
            Txn["maxFeePerGas"] = f'{Web3.from_wei(Txn["maxFeePerGas"],"gwei")} Gwei'
            Txn["maxPriorityFeePerGas"] = f'{Web3.from_wei(Txn["maxPriorityFeePerGas"],"gwei")} Gwei'
            logger.info(f"\n[Account][SendTransaction][EIP-1559]\n[Txn]{dumps(Txn, indent=2)}\n{'-'*80}")
            if self._Request:
                logger.warning(f"\n[Account][RequestAuthorizationBeforeSendTransaction][True]\nDo you confirm sending this transaction?")
                Command = input("Command Input (yes/1/[Enter] or no/0):")
                if Command == "no" or Command == "0" or (len(Command) > 0 and Command != "yes" and Command != "1"):
                    raise Exception("Cancel sending transaction.")
            print("pending...")
            TransactionHash = self._Eth.send_raw_transaction(SignedTxn.rawTransaction).hex()
            TransactionInformation = self._Chain.GetTransactionInformationByHash(TransactionHash)
            return TransactionInformation
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Account][SendTransaction][EIP-1559]Failed\n[From]{From}\n[To]{To}\n[Value]{Value}\n[BaseFee]{BaseFee}\n[MaxPriorityFee]{MaxPriorityFee}\n[GasLimit]{GasLimit}\n[Data]{Data}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def DeployContract(self, ABI: dict, Bytecode: str, Value: int = 0, GasPrice: Optional[int] = None, *Arguments: Optional[Any]) -> dict:
        """
        部署合约。若 120 秒内交易未确认则作超时处理。

        参数：
            ABI (dict): 合约 ABI
            Bytecode (str): 合约部署字节码。
            Value (可选)(int): 随交易发送给合约的网络原生代币数量，单位为 wei ，默认为 0 wei 。
            GasPrice (可选)(Optional[int]): Gas 价格，单位为 wei ，默认使用 RPC 建议的 gas_price 。
            *Arguments (可选)(Optional[Any]): 传给合约构造函数的参数，默认为空。

        返回值：
            TransactionInformation (dict): 交易信息构成的字典，通过 Chain.GetTransactionInformationByHash 获取。当出现异常时返回 None 。
            当合约部署成功时，字典中会额外添加"Contract"字段，该变量是已实例化的 Contract 对象，若失败则为 None。
        """

        try:
            DeployingContract = self._Eth.contract(abi=ABI, bytecode=Bytecode)
            TransactionData = DeployingContract.constructor(*Arguments).build_transaction({"value": Value, "gasPrice": GasPrice if GasPrice else self._Eth.gas_price})
            Txn = {
                "chainId": self._Chain.ChainId,
                "from": self.EthAccount.address,
                "value": TransactionData["value"],
                "gas": TransactionData["gas"],
                "gasPrice": TransactionData["gasPrice"],
                "nonce": self._Eth.get_transaction_count(self.EthAccount.address),
                "data": TransactionData["data"]
            }
            SignedTxn = self.EthAccount.sign_transaction(Txn)
            Txn["gasPrice"] = f'{Web3.from_wei(Txn["gasPrice"],"gwei")} Gwei'
            logger.info(f"\n[Account][DeployContract]\n[Txn]{dumps(Txn, indent=2)}\n{'-'*80}")
            if self._Request:
                logger.warning(f"\n[Account][RequestAuthorizationBeforeSendTransaction][True]\nDo you confirm sending this transaction?")
                Command = input("Command Input (yes/1/[Enter] or no/0):")
                if Command == "no" or Command == "0" or (len(Command) > 0 and Command != "yes" and Command != "1"):
                    raise Exception("Cancel sending transaction.")
            print("pending...")
            TransactionHash = self._Eth.send_raw_transaction(SignedTxn.rawTransaction).hex()
            TransactionInformation = self._Chain.GetTransactionInformationByHash(TransactionHash)
            if TransactionInformation["Status"]:
                DeployedContract = Contract(self, TransactionInformation["ContractAddress"], ABI)
                TransactionInformation["Contract"] = DeployedContract
                return TransactionInformation
            else:
                TransactionInformation["Contract"] = None
                return TransactionInformation
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Account][DeployContract]Failed\n[Value]{Value}\n[GasPrice]{GasPrice}\n[ABI]{ABI}\n[Bytecode]{Bytecode}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def DeployContractWithoutABI(self, Bytecode: str, Value: int = 0, GasPrice: Optional[int] = None, GasLimit: int = 5000000) -> dict:
        """
        在没有 ABI 的情况下，仅使用字节码来部署合约。若 120 秒内交易未确认则作超时处理。

        参数：
            Bytecode (str): 合约部署字节码。
            Value (可选)(int): 随交易发送给合约的网络原生代币数量，单位为 wei ，默认为 0 wei 。
            GasPrice (可选)(Optional[int]): Gas 价格，单位为 wei ，默认使用 RPC 建议的 gas_price 。
            GasLimit (可选)(int): Gas 最大使用量，单位为 wei ，默认为 5000000 wei 。

        返回值：
            TransactionInformation (dict): 交易信息构成的字典，通过 Chain.GetTransactionInformationByHash 获取。当出现异常时返回 None 。
        """

        try:
            Txn = {
                "chainId": self._Chain.ChainId,
                "from": self.EthAccount.address,
                "value": Value,
                "gas": GasLimit,
                "gasPrice": GasPrice if GasPrice else self._Eth.gas_price,
                "nonce": self._Eth.get_transaction_count(self.EthAccount.address),
                "data": Bytecode,
            }
            SignedTxn = self.EthAccount.sign_transaction(Txn)
            Txn["gasPrice"] = f'{Web3.from_wei(Txn["gasPrice"],"gwei")} Gwei'
            logger.info(f"\n[Account][DeployContractWithoutABI]\n[Txn]{dumps(Txn, indent=2)}\n{'-'*80}")
            if self._Request:
                logger.warning(f"\n[Account][RequestAuthorizationBeforeSendTransaction][True]\nDo you confirm sending this transaction?")
                Command = input("Command Input (yes/1/[Enter] or no/0):")
                if Command == "no" or Command == "0" or (len(Command) > 0 and Command != "yes" and Command != "1"):
                    raise Exception("Cancel sending transaction.")
            print("pending...")
            TransactionHash = self._Eth.send_raw_transaction(SignedTxn.rawTransaction).hex()
            TransactionInformation = self._Chain.GetTransactionInformationByHash(TransactionHash)
            return TransactionInformation
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Account][DeployContractWithoutABI]Failed\n[Value]{Value}\n[GasPrice]{GasPrice}\n[GasLimit]{GasLimit}\n[Bytecode]{Bytecode}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def SignMessage(self, Message: str) -> dict:
        """
        消息字符串进行签名。

        参数：
            Message (str): 待签名消息字符串

        返回值：
            SignatureData (str): 签名数据构成的字典。当出现异常时返回 None 。
            {"Address"|"Message"|"MessageHash"|"Signature"|"R"|"S"|"V"}
        """

        try:
            from eth_account.messages import encode_defunct
            SignedMessage = self.EthAccount.sign_message(encode_defunct(text=Message))
            MessageHash, Signature, R, S, V = SignedMessage.messageHash.hex(), SignedMessage.signature.hex(), f"0x{int(hex(SignedMessage.r), 16):0>64x}", f"0x{int(hex(SignedMessage.s), 16):0>64x}", SignedMessage.v
            logger.success(
                f"\n[Account][SignMessage]\n[Address] {self.EthAccount.address}\n[Message] {Message}\n[MessageHash] {MessageHash}\n[Signature] {Signature}\n[R] {R}\n[S] {S}\n[V] {V}\n{'-'*80}"
            )
            SignatureData = {
                "Address": self.EthAccount.address,
                "Message": Message,
                "MessageHash": MessageHash,
                "Signature": Signature,
                "R": R,
                "S": S,
                "V": V
            }
            return SignatureData
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Account][SignMessage]Failed to sign message\n[Address]{self.EthAccount.address}\n[Message]{Message}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def SignMessageHash(self, MessageHash: str) -> dict:
        """
        对消息哈希进行签名。

        参数：
            MessageHash (str): 待签名消息哈希

        返回值：
            SignatureData (str): 签名数据构成的字典。当出现异常时返回 None 。
            {"Address"|"MessageHash"|"Signature"|"R"|"S"|"V"}
        """

        try:
            SignedMessage = self.EthAccount.signHash(MessageHash)
            Signature, R, S, V = SignedMessage.signature.hex(), f"0x{int(hex(SignedMessage.r), 16):0>64x}", f"0x{int(hex(SignedMessage.s), 16):0>64x}", SignedMessage.v
            logger.success(
                f"\n[Account][SignMessageHash]\n[Address] {self.EthAccount.address}\n[MessageHash] {MessageHash}\n[Signature] {Signature}\n[R] {R}\n[S] {S}\n[V] {V}\n{'-'*80}"
            )
            SignatureData = {
                "Address": self.EthAccount.address,
                "MessageHash": MessageHash,
                "Signature": Signature,
                "R": R,
                "S": S,
                "V": V
            }
            return SignatureData
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Account][SignMessageHash]Failed\n[Address]{self.EthAccount.address}\n[MessageHash]{MessageHash}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    def GetRawTransaction(self, To: str, Value: int, Data: str = "0x", GasPrice: Optional[int] = None, GasLimit: int = 100000)-> str:
        """
        获取交易的 RawTransaction

        参数：
            To: 交易对象地址
            Value: 金额
            Data: 参数
            GasPrice:
            GasLimit:

        返回值：
            RawTransaction
        """

        try:
            From = self.EthAccount.address
            To = Web3.to_checksum_address(To)
            Txn = {
                "chainId": self._Chain.ChainId,
                "from": From,
                "to": To,
                "value": Value,
                "gas": GasLimit,
                "gasPrice": GasPrice if GasPrice else self._Eth.gas_price,
                "nonce": self._Eth.get_transaction_count(From),
                "data": Data,
            }
            SignedTxn = self.EthAccount.sign_transaction(Txn)
            logger.success(
                f"\n[Account][GetRawTransaction]\n[RawTransaction] {SignedTxn.rawTransaction.hex()}\n{'-'*80}")
            return SignedTxn.rawTransaction.hex()

        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Account][GetRawTransaction] Failed to get RawTransaction{ExceptionInformation}{'-'*80}"
            )
            return None

class Contract():
    """
    Contract 是合约实例，作为与指定合约进行交互的基础。
    """

    def __init__(self, Account: Account, Address: str, ABI: dict):
        """
        初始化。通过合约地址与 ABI 来实例化合约，并与 Account 绑定，后续所有对该合约的调用都会由这一账户发起。当合约实例化失败时会抛出异常。

        参数：
            Account (Poseidon.Blockchain.Account): 账户实例
            Address (str): 合约地址
            ABI (str): 合约 ABI

        成员变量：
            Instance (Web3.eth.Contract): web3.py 原生 contract 对象实例
            Address (str): 合约地址
        """

        try:
            self._Account, self._Eth, self.Address = Account, Account._Eth, Web3.to_checksum_address(Address)
            self.Instance = self._Eth.contract(address=self.Address, abi=ABI)
            logger.success(f"\n[Contract][Initialize] Successfully instantiated contract [{self.Address}]\n{'-'*80}")
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Contract][Initialize]Failed to instantiated contract [{self.Address}]\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            raise Exception("Failed to instantiate contract.")

    def CallFunction(self, FunctionName: str, *FunctionArguments: Optional[Any]) -> dict:
        """
        通过传入函数名及参数来调用该合约内的函数。

        参数：
            FunctionName (str): 函数名称
            *FunctionArguments (可选)(Optional[Any]): 函数参数，默认为空。

        返回值：
            TransactionInformation (dict): 交易信息构成的字典，通过 Chain.GetTransactionInformationByHash 获取。当出现异常时返回 None 。

        例子：
            FunctionName: FunctionName=setX, *FunctionArguments=101
        """

        TransactionData = self.Instance.functions[FunctionName](*FunctionArguments).build_transaction({"gasPrice": self._Eth.gas_price})
        logger.info(f"\n[Contract][CallFunction]\n[ContractAddress] {self.Address}\n[Function] {FunctionName}{FunctionArguments}\n{'-'*80}")
        TransactionInformation = self._Account.SendTransaction(self.Address, TransactionData["data"], TransactionData["value"], TransactionData['gasPrice'], TransactionData["gas"])
        return TransactionInformation

    def CallFunctionWithParameters(self, Value: int, GasPrice: Optional[int], GasLimit: int, FunctionName: str, *FunctionArguments: Optional[Any]) -> dict:
        """
        通过传入函数名及参数来调用该合约内的函数。支持自定义 Value 和 GasLimit 。

        参数：
            Value (int): 随交易发送的网络原生代币数量，单位为 wei 。
            GasPrice (Optional[int]): Gas 价格，单位为 wei ，默认使用 RPC 建议的 gas_price 。
            GasLimit (int): Gas 最大使用量，单位为 wei 。
            FunctionName (str): 函数名称
            *FunctionArguments (Optional[Any]): 函数参数，默认为空。

        返回值：
            TransactionInformation (dict): 交易信息构成的字典，通过 Chain.GetTransactionInformationByHash 获取。当出现异常时返回 None 。
        """

        TransactionData = self.Instance.functions[FunctionName](*FunctionArguments).build_transaction({"value": Value, "gasPrice": GasPrice if GasPrice else self._Eth.gas_price, "gas": GasLimit})
        logger.info(
            f"\n[Contract][CallFunctionWithValueAndGasLimit]\n[ContractAddress] {self.Address}\n[Function] {FunctionName}{FunctionArguments}\n[Value] {TransactionData['value']}\n[GasPrice] {TransactionData['gasPrice']}\n[GasLimit] {TransactionData['gas']}\n{'-'*80}"
        )
        TransactionInformation = self._Account.SendTransaction(self.Address, TransactionData["data"], TransactionData["value"], TransactionData['gasPrice'], TransactionData["gas"])
        return TransactionInformation

    def ReadOnlyCallFunction(self, FunctionName: str, *FunctionArguments: Optional[Any]) -> Any:
        """
        通过传入函数名及参数来调用该合约内的只读函数。

        参数：
            FunctionName (str): 函数名称
            *FunctionArguments (可选)(Optional[Any]): 函数参数，默认为空。

        返回值：
            Result (Any): 调用函数后得到的返回值。当出现异常时返回 None 。
        """

        try:
            Result = self.Instance.functions[FunctionName](*FunctionArguments).call()
            logger.success(
                f"\n[Contract][ReadOnlyCallFunction]\n[ContractAddress] {self.Address}\n[Function] {FunctionName}{FunctionArguments}\n[Result] {Result}\n{'-'*80}"
            )
            return Result
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Contract][ReadOnlyCallFunction]Failed\n[ContractAddress] {self.Address}\n[Function] {FunctionName}{FunctionArguments}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    def EncodeABI(self, FunctionName: str, *FunctionArguments: Optional[Any]) -> str:
        """
        通过传入函数名及参数进行编码，相当于生成调用该函数的 CallData 。

        参数：
            FunctionName (str): 函数名称
            *FunctionArguments (可选)(Optional[Any]): 函数参数，默认为空。

        返回值：
            CallData (str): 调用数据编码。含 0x 前缀的十六进制形式。当出现异常时返回 None 。
        """

        try:
            CallData = self.Instance.encodeABI(fn_name=FunctionName, args=FunctionArguments)
            logger.success(
                f"\n[Contract][EncodeABI]\n[ContractAddress] {self.Address}\n[Function] {FunctionName}{FunctionArguments}\n[CallData] {CallData}\n{'-'*80}"
            )
            return CallData
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Contract][EncodeABI]Failed\n[ContractAddress] {self.Address}\n[Function] {FunctionName}{FunctionArguments}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    def DecodeFunctionInputData(self, InputData: str) -> tuple:
        """
        解码对当前合约执行调用的 InputData ，得出所调用的函数及其参数值。

        参数：
            InputData (str): 对当前合约执行调用的 InputData

        返回值：
            Result (tuple): 函数及其参数值
        """

        try:
            Result = self.Instance.decode_function_input(InputData)
            logger.success(
                f"\n[Contract][DecodeFunctionInputData]\n[InputData] {InputData}\n[Function] {Result[0]}\n[Parameters] {Result[1]}\n{'-'*80}"
            )
            return Result
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[Contract][DecodeFunctionInputData]Failed\n[InputData] {InputData}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

class BlockchainUtils():
    """
    通用工具集，整合了常用的链下操作。静态类，无需实例化。
    """
    @staticmethod
    def abiToInterface():
        """
        不会，先挖个坑
        在线平台：https://gnidan.github.io/abi-to-sol/
        GitHub：https://github.com/gnidan/abi-to-sol
        """
        pass

    @staticmethod
    def randomSign(privateKey:str, Message:str):
        """
        privateKey: 私钥
        Message：待签名的消息
        让临时密钥随机取值，因此相同的私钥对相同的消息进行签名，得可以得到不一样的结果
        """
        current_directory = os.path.dirname(os.path.abspath(__file__))
        with open(f'{current_directory}/JSTools.js', 'r', encoding='UTF-8') as f:
            js_code = f.read()
        context = execjs.compile(js_code)
        result = context.call("randomSign", privateKey, Message)
        logger.success(
            f"\n[BlockchainUtils][Compile]\n[privateKey]{privateKey}\n[signature]{result}\n{'-' * 80}"
        )
        return result

    @staticmethod
    def ABIEncoder():
        """
        用这个在线工具更加方便：https://abi.hashex.org/
        形参类型和数据  ==>  calldata
        """
        pass

    @staticmethod
    def SwitchSolidityVersion(SolidityVersion: str):
        """
        设置当前使用的 Solidity 版本，若该版本未安装则会自动安装。

        参数：
            SolidityVersion (str): Solidity 版本号
        """

        try:
            from solcx import install_solc, set_solc_version, get_solc_version
            install_solc(SolidityVersion)
            set_solc_version(SolidityVersion)
            SolidityVersion = get_solc_version(True)
            logger.success(f"\n[BlockchainUtils][SwitchSolidityVersion] Current Solidity Version [{SolidityVersion}]\n{'-'*80}")
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][SwitchSolidityVersion]Failed to switch to version [{SolidityVersion}]\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )

    @staticmethod
    def Compile(FileCourse: str, ContractName: str, SolidityVersion: Optional[str] = None, AllowPaths: Optional[str] = None, Optimize: bool = False) -> tuple:
        """
        根据给定的参数使用 py-solc-x 编译合约。当编译失败时会抛出异常。

        参数：
            FileCourse (str): 合约文件完整路径。当合约文件与脚本文件在同一目录下时可直接使用文件名。
            ContractName (str): 要编译的合约名称
            SolidityVersion (可选)(Optional[str]): 指定使用的 Solidity 版本。若不指定则会使用当前已激活的 Solidity 版本进行编译。默认为 None 。
            AllowPaths (可选)(Optional[str]): 指定许可路径。在编译时可能会出现 AllowPaths 相关错误可在这里解决。默认为 None 。
            Optimize (可选)(bool): 是否开启优化器。默认为 False 。

        返回值：
            (ABI, Bytecode) (tuple): 由 ABI 和 Bytecode 组成的元组
        """

        try:
            from solcx import compile_source
            with open(FileCourse, "r", encoding="utf-8") as sol:
                CompiledSol = compile_source(sol.read(), solc_version=SolidityVersion, allow_paths=AllowPaths, optimize=Optimize, output_values=['abi', 'bin'])
            ContractData = CompiledSol[f'<stdin>:{ContractName}']
            ABI, Bytecode = ContractData['abi'], ContractData['bin']
            if not os.path.exists("../output/"):
                os.makedirs("../output/")
            with open(f'../output/{ContractName}_ABI.json', 'w', encoding="utf-8") as f:
                dump(ABI, f, indent=4)
            with open(f'../output/{ContractName}_BYTECODE.json', 'w', encoding="utf-8") as f:
                dump(Bytecode, f, indent=4)
            logger.success(
                f"\n[BlockchainUtils][Compile]\n[FileCourse]{FileCourse}\n[ContractName]{ContractName}\n[ABI]{ABI}\n[Bytecode]{Bytecode}\n{'-'*80}"
            )
            return (ABI, Bytecode)
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][Compile]Failed\n[FileCourse]{FileCourse}\n[ContractName]{ContractName}\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            raise Exception("Failed to compile the contract.")

    @staticmethod
    def MnemonicToAddressAndPrivateKey(Mnemonic: str) -> tuple:
        """
        将助记词转换为账户地址与私钥。参考 BIP-39 标准。

        参数：
            Mnemonic (str): 助记词字符串。以空格进行分隔。

        返回值：
            (Address, PrivateKey) (tuple): 由账户地址和私钥组成的元组。当出现异常时返回 None 。
        """

        try:
            EthAccount.enable_unaudited_hdwallet_features()
            Temp = EthAccount.from_mnemonic(Mnemonic)
            Address, PrivateKey = Web3.to_checksum_address(Temp.address), Temp.key.hex()
            logger.success(
                f"\n[BlockchainUtils][MnemonicToAddressAndPrivateKey]\n[Mnemonic] {Mnemonic}\n[Address] {Address}\n[PrivateKey] {PrivateKey}\n{'-'*80}"
            )
            return (Address, PrivateKey)
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][MnemonicToAddressAndPrivateKey]Failed\n[Mnemonic] {Mnemonic}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def AssemblyToBytecode(Assembly: str) -> str:
        """
        将 EVM Assembly 转为 EVM Bytecode 。

        参数：
            Assembly (str): EVM Assembly

        返回值：
            Bytecode (str): EVM Bytecode 。含 0x 前缀的六进制形式。当出现异常时返回 None 。

        例子：
             PUSH1 0x60\n BLOCKHASH\n MSTORE\n PUSH1 0x2\n PUSH2 0x100\n

            "0x606040526002610100"
        """

        try:
            from pyevmasm import assemble_hex
            Bytecode = assemble_hex(Assembly)
            logger.success(f"\n[BlockchainUtils][AssemblyToBytecode]\n[Bytecode] {Bytecode}\n{'-'*80}")
            return Bytecode
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][AssemblyToBytecod] Failed\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def BytecodeToAssembly(Bytecode: str) -> str:
        """
        将 EVM Bytecode 转为 EVM Assembly 。

        参数：
            Bytecode (str): EVM Bytecode 。含 0x 前缀的十六进制形式。

        返回值：
            Assembly (str): EVM Assembly 。当出现异常时返回 None 。
        """

        try:
            from pyevmasm import disassemble_hex
            Assembly = disassemble_hex(Bytecode)
            logger.success(f"\n[BlockchainUtils][AssemblyToBytecode]\n[Assembly]\n{Assembly}\n{'-'*80}")
            return Assembly
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][BytecodeToAssembly]Failed\n[ExceptionInformation]{ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def SignatureToRSV(Signature: str) -> dict:
        """
        将签名解析成 R S V 。

        参数：
            Signature (str): 签名。含 0x 前缀的十六进制形式。

        返回值：
            Result (dict): 解析结果。当出现异常时返回 None 。
            {"Signature"|"R"|"S"|"V"}
        """

        try:
            Signature = hex(int(Signature, 16))
            assert (len(Signature) == 130 + 2)
            R, S, V = '0x' + Signature[2:66], '0x' + Signature[66:-2], '0x' + Signature[-2:]
            logger.success(f"\n[BlockchainUtils][SignatureToRSV]\n[Signature] {Signature}\n[R] {R}\n[S] {S}\n[V] {V}\n{'-'*80}")
            Result = {
                "Signature": Signature,
                "R": R,
                "S": S,
                "V": V
            }
            return Result
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][SignatureToRSV]Failed\n[Signature] {Signature}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def RSVToSignature(R: str, S: str, V: str) -> dict:
        """
        将 R S V 合并成签名。

        参数：
            R (str): 签名 r 值。含 0x 前缀的十六进制形式。
            S (str): 签名 s 值。含 0x 前缀的十六进制形式。
            V (int): 签名 v 值。含 0x 前缀的十六进制形式。

        返回值：
            Result (dict): 合并结果。当出现异常时返回 None 。
            {"Signature"|"R"|"S"|"V"}
        """

        try:

            R, S, V = hex(int(R, 16)), hex(int(S, 16)), hex(int(V, 16))
            assert (len(R) == 64 + 2 and len(S) == 64 + 2 and len(V) == 2 + 2)
            Signature = '0x' + R[2:] + S[2:] + V[2:]
            logger.success(f"\n[BlockchainUtils][RSVToSignature]\n[R] {R}\n[S] {S}\n[V] {V}\n[Signature] {Signature}\n{'-'*80}")
            Result = {
                "Signature": Signature,
                "R": R,
                "S": S,
                "V": V
            }
            return Result
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][RSVToSignature] Failed\n[R] {R}\n[S] {S}\n[V] {V}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def GetFunctionSelector(FunctionName: str, FunctionParameters: Optional[List[str]] = []) -> str:
        """
        获取四字节函数选择器。

        参数：
            FunctionName (str): 函数名称。
            FunctionParameters (可选)(Optional[List[str]]): 函数参数列表。默认为空。

        返回值：
            Result (str): 四字节函数选择器。含 0x 前缀的十六进制形式

        例子：
            1. setX(uint256,uint256): GetFunctionSelector("setX",["uint256","uint256"])
            2. getX():                GetFunctionSelector("getX",[])
        """

        try:
            FunctionSelector = Web3.keccak(f"{FunctionName}({','.join(FunctionParameters)})".encode())[:4].hex()
            logger.success(f"\n[BlockchainUtils][GetFunctionSelector]\n[FunctionName] {FunctionName}\n[FunctionParameters] {FunctionParameters}\n[FunctionSelector] {FunctionSelector}\n{'-'*80}")
            return FunctionSelector
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][GetFunctionSelector] Failed\n[FunctionName] {FunctionName}\n[FunctionParameters] {FunctionParameters}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def RecoverMessage(Message: str, Signature: str) -> str:
        """
        通过消息原文和签名还原出签署者的账户地址。

        参数：
            Message (str): 消息原文
            Signature (str): 签名

        返回值：
            Signer (str): 签署者的账户地址。当出现异常时返回 None 。
        """
        MessageHash = Web3.keccak(f"{Message}".encode()).hex()
        try:
            Signer = EthAccount._recover_hash(MessageHash, signature=Signature)
            logger.success(
                f"\n[BlockchainUtils][RecoverMessage]\n[Message] {Message}\n[MessageHash] {MessageHash}\n[Signature] {Signature}\n[Signer] {Signer}\n{'-'*80}"
            )
            return Signer
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][RecoverMessage] Failed\n[MessageHash] {MessageHash}\n[Signature] {Signature}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def RecoverMessageHash(MessageHash: str, Signature: str) -> str:
        """
        通过消息哈希和签名还原出签署者的账户地址。

        参数：
            MessageHash (str): 消息哈希
            Signature (str): 签名

        返回值：
            Signer (str): 签署者的账户地址。当出现异常时返回 None 。
        """

        try:
            Signer = EthAccount._recover_hash(MessageHash, signature=Signature)
            logger.success(
                f"\n[BlockchainUtils][RecoverMessageByHash]\n[MessageHash] {MessageHash}\n[Signature] {Signature}\n[Signer] {Signer}\n{'-'*80}"
            )
            return Signer
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][RecoverMessageByHash] Failed\n[MessageHash] {MessageHash}\n[Signature] {Signature}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def RecoverRawTransaction(RawTransactionData: str) -> str:
        """
        获取签署此交易的账户地址。

        参数：
            RawTransactionData (str): 原生交易数据。含 0x 前缀的十六进制形式。

        返回值：
            Address (str): 账户地址。当出现异常时返回 None 。

        例子：
            BlockchainUtils.RecoverRawTransaction('0x???????????????????????????????????????????????????????????????????53360025f6101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550348015610058575f80fd5b5061060d806100665f395ff3fe608060405234801561000f575f80fd5b506004361061009c575f3560e01c80635197c7aa116100645780635197c7aa1461015a5780638da5cb5b14610178578063a56dfe4a14610196578063f077b408146101b4578063f7c86c43146101e45761009c565b80630c55699c146100a057806336789135146100be5780633ae8ca5b146100dc5780633d308b8c146100fa5780634018d9aa1461012a575b5f80fd5b6100a8610202565b6040516100b591906102f9565b60405180910390f35b6100c6610207565b6040516100d3919061032a565b60405180910390f35b6100e461022e565b6040516100f1919061037d565b60405180910390f35b610114600480360381019061010f91906104e3565b610255565b6040516101219190610569565b60405180910390f35b610144600480360381019061013f91906105ac565b610267565b60405161015191906102f9565b60405180910390f35b610162610277565b60405161016f91906102f9565b60405180910390f35b61018061027f565b60405161018d9190610569565b60405180910390f35b61019e6102a4565b6040516101ab91906102f9565b60405180910390f35b6101ce60048036038101906101c991906104e3565b6102aa565b6040516101db919061032a565b60405180910390f35b6101ec6102ba565b6040516101f9919061037d565b60405180910390f35b5f5481565b5f7f1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8905090565b5f7f3b87482a78e5b630e53cdef10dee5ef1d808954ea4d135fc4081b08d5f6bb152905090565b5f81805190602001205f1c9050919050565b5f815f819055505f549050919050565b5f8054905090565b60025f9054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60015481565b5f81805190602001209050919050565b5f7f5197c7aa08bba9fc76e885f80f9fae33e8ebd06ccfa0935ca9ce2031d9dfb713905090565b5f819050919050565b6102f3816102e1565b82525050565b5f60208201905061030c5f8301846102ea565b92915050565b5f819050919050565b61032481610312565b82525050565b5f60208201905061033d5f83018461031b565b92915050565b5f7fffffffff0000000000000000000000000000000000000000000000000000000082169050919050565b61037781610343565b82525050565b5f6020820190506103905f83018461036e565b92915050565b5f604051905090565b5f80fd5b5f80fd5b5f80fd5b5f80fd5b5f601f19601f8301169050919050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52604160045260245ffd5b6103f5826103af565b810181811067ffffffffffffffff82111715610414576104136103bf565b5b80604052505050565b5f610426610396565b905061043282826103ec565b919050565b5f67ffffffffffffffff821115610451576104506103bf565b5b61045a826103af565b9050602081019050919050565b828183375f83830152505050565b5f61048761048284610437565b61041d565b9050828152602081018484840111156104a3576104a26103ab565b5b6104ae848285610467565b509392505050565b5f82601f8301126104ca576104c96103a7565b5b81356104da848260208601610475565b91505092915050565b5f602082840312156104f8576104f761039f565b5b5f82013567ffffffffffffffff811115610515576105146103a3565b5b610521848285016104b6565b91505092915050565b5f73ffffffffffffffffffffffffffffffffffffffff82169050919050565b5f6105538261052a565b9050919050565b61056381610549565b82525050565b5f60208201905061057c5f83018461055a565b92915050565b61058b816102e1565b8114610595575f80fd5b50565b5f813590506105a681610582565b92915050565b5f602082840312156105c1576105c061039f565b5b5f6105ce84828501610598565b9150509291505056fea2646970667358221220c18bd28ffd96e5832c46c7dfc107a769979b570510100271e4528db034229fad64736f6c634300081400332ea0f900f58e0575999bf71532cdf7de3ccff657ceff7cb613481c2d10074a70a757a0684dd76b2e4c902bd7f2d951bc96b79ea56599ac3aa91dc86770a1de43257336')
            如何获取 RawTransaction呢？
        """

        try:
            Address = EthAccount.recover_transaction(RawTransactionData)
            logger.success(f"\n[BlockchainUtils][RecoverRawTransaction]\n[RawTransactionData] {RawTransactionData}\n[Address] {Address}\n{'-'*80}")
            return Address
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][RecoverRawTransaction]Failed\n[RawTransactionData] {RawTransactionData}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def CrackSelector(source_function_name, source_param_types, target_param_types):
        """
        根据源函数名、参数与想要碰撞生成的函数的参数，碰撞生成出一个函数名，以使得这两个函数的选择器签名相等。

        参数：
            source_function_name (str): 源函数名
            source_param_types (List[str]): 源函数参数列表
            target_param_types (List[str]): 想要碰撞生成的函数的参数列表

        返回值：
            ToGenerateFunction (str): 碰撞出的函数的名称与参数完整表示。当出现异常时返回 None 。

        编者注：
            我不知道如何使用这个函数，如果想用这个功能，可以尝试以下网站：
                1. https://www.4byte.directory/
                2. https://sig.eth.samczsun.com/
                3. https://github.com/AmazingAng/power-clash
            或者使用方法 CrackSelector_chatGPT 来尝试
        """
        try:
            function_ = f"{source_function_name}({','.join(source_param_types)})"
            function_hash = Web3.keccak(f"{function_}".encode()).hex()

            count = 0
            salt = 0

            logger.success(
                f"\n[BlockchainUtils][CrackSelector]\n[goalSig] {str(function_hash[:10])}\n start crack... \n{'-' * 80}"
            )


            while(True):
                name = "LEVI_"+str(salt)
                function_name = f"{name}({','.join(target_param_types)})"
                if(str(function_hash[:10]) == str(Web3.keccak(f"{function_name}".encode()).hex()[:10])):
                    logger.success(
                        f"\n[BlockchainUtils][CrackSelector]\n[function_name] {function_name}\n{'-' * 80}"
                    )
                    return function_name
                count = count+1
                salt = salt + 1
                if(count % 100000 == 0):
                    print("this time:",str(Web3.keccak(f"{function_name}".encode()).hex()[:10]))
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][CrackSelector]Failed\n[function_name] {function_name}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def GetContractAddressByCREATE(Deployer: str, Nonce: int) -> str:
        """
        获取某账户以 CREATE 方式部署的合约的地址。

        参数：
            Deployer (str): 部署者地址
            Nonce (int): 部署者发送合约部署交易的 nonce 值

        返回值：
            Address (str): 计算出的合约地址
        """

        try:
            Address = utils.address.get_create_address(Deployer, Nonce)
            logger.success(
                f"\n[BlockchainUtils][GetContractAddressByCREATE]\n[Deployer] {Deployer}\n[Nonce] {Nonce}\n[ContractAddress] {Address}\n{'-'*80}"
            )
            return Address
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][GetContractAddressByCREATE]Failed\n[Deployer] {Deployer}\n[Nonce] {Nonce}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def GetContractAddressByCREATE2(Deployer: str, Salt: str, CreationCode: str) -> str:
        """
        获取某合约账户以 CREATE2 方式部署的另一个合约的地址。

        参数：
            Deployer (str): 部署者地址
            Salt (str): 盐值
            CreationCode (str): 合约的创建时字节码

        返回值：
            Address (str): 计算出的合约地址
        """

        try:
            Address = utils.address.get_create2_address(Deployer, Salt, CreationCode)
            logger.success(
                f"\n[BlockchainUtils][GetContractAddressByCREATE2]\n[Deployer] {Deployer}\n[Salt] {Salt}\n[CreationCode] {CreationCode}\n[ContractAddress] {Address}\n{'-'*80}"
            )
            return Address
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][GetContractAddressByCREATE2] Failed\n[Deployer] {Deployer}\n[Salt] {Salt}\n[CreationCode] {CreationCode}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def Keccak256(content: str) -> str:
        """
        对内容进行 keccak256加密

        参数：
            content： 加密内容

        返回值：
            str： 加密过后的 hash值
        """
        hash = Web3.keccak(f"{content}".encode()).hex()
        logger.success(
            f"\n[BlockchainUtils][Keccak256]\n[content] {content}\n[hash] {hash}\n{'-' * 80}")
        return hash

    @staticmethod
    def GetPublicKeyFromPrivateKey(private_key: str) -> str:
        """
        根据私钥来获得公钥

        参数：
            private_key：私钥，十六进制

        返回值：
            str： 公钥，带有 '0x' 开头的十六进制值
        """

        try:
            private_key_bytes = unhexlify(private_key)
            public_key = PublicKey.from_valid_secret(private_key_bytes).format(compressed=False)[1:]

            logger.success(
                f"\n[BlockchainUtils][GetPublicKeyFromPrivateKey]\n[privateKey] {private_key}\n[publicKey] 0x{hexlify(public_key).decode()}\n{'-' * 80}")
            return '0x' + hexlify(public_key).decode()
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][GetPublicKeyFromPrivateKey] Failed\n[privateKey] {private_key}\n {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def GetAddressFromPublicKey(publicKey: str) -> str:
        """
        根据公钥来获得地址

        参数：
            publicKey：公钥，十六进制

        返回值：
            str： 地址，带有 '0x' 开头的十六进制值
        """

        try:
            public_key_bytes = bytes.fromhex(publicKey[2:])
            keccak_hash = keccak(public_key_bytes)
            address = keccak_hash[-20:].hex()

            logger.success(
                f"\n[BlockchainUtils][GetAddressFromPublicKey]\n[publicKey] {publicKey}\n[address] {address}\n{'-' * 80}")
            return address
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][GetAddressFromPublicKey] Failed\n[publicKey] {publicKey}\n {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def GweiToWei(Value: Union[int, float]) -> int:
        """
        将一个正整数或浮点数按照 Gwei 为单位直接转化为 wei 为单位的正整数。即假设传入 Value = 1，将返回 1000000000 。

        参数：
            Value (Union[int,float]): 假设以 Gwei 为单位的待转换值。

        返回值：
            Result (int): 已转换为以 wei 为单位的值。当出现异常时返回 None 。
        """

        try:
            assert(Value > 0)
            return int(Value * 10**9)
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][GweiToWei] Failed\n[Value] {Value}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def EtherToWei(Ether: float) -> int:
        """
        将一个浮点数 Ether转换为 Wei
        """
        try:
            assert(Ether > 0)
            logger.success(
                f"\n[BlockchainUtils][EtherToWei] [Value] {int(Ether * 1e18)}\n{'-'*80}"
            )
            return int(Ether * 1e18)
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][EtherToWei] Failed\n[Value] {Ether}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def WeiToEther(Wei: int) -> float:
        """
        将一个整数 Wei 转换为 Ether
        """
        try:
            assert(Wei > 0)
            logger.success(
                f"\n[BlockchainUtils][EtherToWei] [Value] {float(Wei / 1e18)}\n{'-'*80}"
            )
            return float(Wei / 1e18)
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][WeiToEther] Failed\n[Value] {Wei}\n[ExceptionInformation] {ExceptionInformation}{'-'*80}"
            )

    @staticmethod
    def AbiToInterface():
        '''
            如何将 ABI的 JSON文件转换为人类可读的 ABI（interface）呢？
            这里有用 JavaScript实现的 : https://github.com/gnidan/abi-to-sol
            如何用 python实现？先挖个坑
        '''
        pass

    @staticmethod
    def GetSpecialAddressByCreate2(DeployAddress: str, BytecodeHash: str, content: str, position:int = 0) -> str:
        '''
        获得包含特定内容的地址，通过 create2。根据 create2原理写出来的
        如果想让地址的某个位置是特定内容的值，
        此方法用于获取一个位置有特殊内容的地址

        参数：
            DeployAttackAddress (str): 部署合约地址
            BytecodeHash (str): 待部署的合约的 bytecode的 hash 值
            content: 包含的某个特定的值
            position(可选)：地址的某个位置是特定内容的值，默认是0，可手动调整，比如 content='ab',position=-2就是计算得到的地址的后两位是'ab'，第position位是之后的

        返回值：
             str: 第一个是 salt值，第二个是地址

        例子： BlockchainUtils.GetSpecialAddressByCreate2("406187E1b3366B5da3539D99C4E88E42FC60De50","da647010355608442b3eab68e7dcc6d5b836f2628d2366ff8ae853413a643965","5a54")
              得到的地址包含 '5a54'
        '''
        try:
            i = 0
            start_time = time.time()  # 获取当前时间戳

            while (1):
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time >= 10:
                    raise Exception("time out,maybe a wrong position")

                salt = hex(i)[2:].rjust(64, '0')
                s = '0xff' + DeployAddress + salt + BytecodeHash
                hashed = Web3.keccak(hexstr=s)
                address = ''.join(['%02x' % b for b in hashed])[24:]
                if position == 0 and content in address[position:position+len(content)]:
                    logger.success(
                        f"\n[BlockchainUtils][GetSpecialAddressByCreate2]\n[content] {content} \n[salt] 0x{salt} \n[position] [{position}:{position+len(content)}) \n[address] 0x{address}\n{'-' * 80}")
                    return "0x" + salt, "0x" + address
                elif position > 0 and content in address[position:position+len(content)]:
                    logger.success(
                        f"\n[BlockchainUtils][GetSpecialAddressByCreate2]\n[content] {content} \n[salt] 0x{salt} \n[position] [{position}:{position+len(content)}) \n[address] 0x{address}\n{'-' * 80}")
                    return "0x" + salt, "0x" + address
                elif position < 0 and position != -4 and content in address[position:position + len(content)]:
                    logger.success(
                        f"\n[BlockchainUtils][GetSpecialAddressByCreate2]\n[content] {content} \n[salt] 0x{salt} \n[position] [{position}:{position + len(content)}) \n[address] 0x{address}\n{'-' * 80}")
                    return "0x" + salt, "0x" + address
                elif position == -4 and content in address[position:]:
                    logger.success(
                        f"\n[BlockchainUtils][GetSpecialAddressByCreate2]\n[content] {content} \n[salt] 0x{salt} \n[position] [{position}:-1] \n[address] 0x{address} \n{'-' * 80}")
                    return "0x" + salt, "0x" + address
                else:
                    pass
                i += 1
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][GetSpecialAddressByCreate2] Failed\n[content] {content}\n {ExceptionInformation}{'-'*80}"
            )
            return None

    @staticmethod
    def GetSpecialAddressByCreate2_two(DeployAddress: str, BytecodeHash: str, content1: str, content2: str, position1: int, position2: int) -> str:
        '''
        获得包含特定内容的地址，通过 create2。根据 create2原理写出来的
        如果想让地址的某个位置是特定内容的值，
        此方法用于获取两个不同位置有特殊内容的地址
        不支持负数索引,总共0~40位

        参数：
            DeployAttackAddress (str): 部署合约地址
            BytecodeHash (str): 待部署的合约的 bytecode的 hash 值
            content1: 包含的某个特定的值
            content1: 包含的某个特定的值
            position1：地址的某个位置是特定内容的值
            position2：地址的某个位置是特定内容的值

        返回值：
             str: 第一个是 salt值，第二个是地址
        '''
        try:
            i = 0
            start_time = time.time()  # 获取当前时间戳

            while (1):
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time >= 10:
                    raise Exception("time out,maybe a wrong position")

                salt = hex(i)[2:].rjust(64, '0')
                s = '0xff' + DeployAddress + salt + BytecodeHash
                hashed = Web3.keccak(hexstr=s)
                address = ''.join(['%02x' % b for b in hashed])[24:]
                if content1 in address[position1:position1 + len(content1)] and content2 in address[position2:position2 + len(content2)]:
                    logger.success(
                        f"\n[BlockchainUtils][GetSpecialAddressByCreate2_two]\n[content1] {content1} \n[position1] [{position1}:{position1 + len(content1)}) \n[content2] {content2} \n[position2] [{position2}:{position2 + len(content2)}) \n[salt] 0x{salt} \n[address] 0x{address}\n{'-' * 80}")
                    return "0x" + salt, "0x" + address
                else:
                    pass
                i += 1
        except Exception:
            ExceptionInformation = format_exc()
            logger.error(
                f"\n[BlockchainUtils][GetSpecialAddressByCreate2_two] Failed\n[content1] {content1} \n[content2] {content2}\n {ExceptionInformation}{'-' * 80}"
            )
            return None

    @staticmethod
    def createEOA():
        '''
        不断生成新的 EOA 账户，可以自己修改源码来获得特殊的私钥、公钥、地址
        '''

        g = ecdsa.generator_secp256k1
        private_key = random.randint(0, 1 << 256 - 1)
        public_key = private_key * g
        x = str(hex(public_key.x())[2:])
        x = ("00" * 32 + x)[-32 * 2:]
        y = str(hex(public_key.y())[2:])
        y = ("00" * 32 + y)[-32 * 2:]
        public_key = x + y
        public_key_bytes = bytes.fromhex(public_key)
        keccak_hash = keccak(public_key_bytes)
        address = keccak_hash[-20:].hex()
        logger.success(f"\n[BlockchainUtils][createEOA]\n[private_key] {hex(private_key)} \n[public_key] 0x{public_key}\n[address] 0x{address}")
        return (hex(private_key), public_key, address)

    @staticmethod
    def signMessage(message:str,pravateKey:str):
        messagehash = Web3.keccak(text=message)
        print("message's hash", messagehash.hex())
        privatekey = pravateKey
        signMessage = EthAccount.signHash(message_hash=messagehash, private_key=privatekey)

        print("signMessage = ", signMessage)
        print("r = ", Web3.to_hex(signMessage.r))
        print("s = ", Web3.to_hex(signMessage.s))
        print("v = ", Web3.to_hex(signMessage.v))
        return (Web3.to_hex(signMessage.r),Web3.to_hex(signMessage.s),Web3.to_hex(signMessage.v))
