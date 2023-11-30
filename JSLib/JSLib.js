// 发送calldata交易
async function sendTransactionExample() {
    const {ethers} = require("ethers")

    // 配置goerli网络提供者
    const provider = ethers.getDefaultProvider("https://eth-goerli.g.alchemy.com/v2/xxxxxxxxxxxxxx");

    // 以太坊钱包私钥
    const privateKey = 'xxxxxxxxxxxxx';

    // 根据私钥创建钱包
    const wallet = new ethers.Wallet(privateKey, provider);

    // 题目地址
    const toAddress = '0x5D342aa5Fb9aa061a90e1D40dE65a8719BbBf014';

    // 要发送的原始数据
    const data = '0x30c13ade0000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000020606e1500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000476227e1200000000000000000000000000000000000000000000000000000000';

    // 创建交易对象
    const transaction = {
      to: toAddress,
      data: data,
    };

  try {
    // 发送交易
    const response = await wallet.sendTransaction(transaction);
    console.log('交易成功:', response.hash);
  } catch (error) {
    console.error('交易失败:', error);
  }

}
