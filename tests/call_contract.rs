use alloy::primitives::address;
use alloy::primitives::utils::format_units;
use alloy::sol;
use coordinate::config;
use dotenv::dotenv;
use std::env;

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IWETH9,
    "assets/abi/IWETH9.json"
);

#[tokio::test]
async fn test_call_eth_bundle() -> Result<(), Box<dyn std::error::Error>> {
    dotenv().ok();
    let etherscan_key = env::var("ETHERSCAN_KEY")?;
    let rpc_url = env::var("RPC_URL")?;
    let private_key = env::var("PRIVATE_KEY")?;
    let config = config::Config::init(private_key, rpc_url, etherscan_key)?;

    let weth_address = address!("C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2");
    let weth_instance = IWETH9::new(weth_address, config.provider);

    let total_supply = weth_instance.totalSupply().call().await?._0;
    println!(
        "WETH Total supply: {:?}",
        format_units(total_supply, "ether")?
    );

    Ok(())
}
