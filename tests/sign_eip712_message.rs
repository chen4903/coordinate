use alloy_primitives::address;
use alloy_primitives::U256;
use coordinate::config;
use coordinate::primitives;
use dotenv::dotenv;
use std::env;

#[tokio::test]
async fn test_call_eth_bundle() -> Result<(), Box<dyn std::error::Error>> {
    dotenv().ok();
    let etherscan_key = env::var("ETHERSCAN_KEY")?;
    let rpc_url = env::var("RPC_URL")?;
    let private_key = env::var("PRIVATE_KEY")?;
    let config = config::Config::init(private_key, rpc_url, etherscan_key).await?;

    let signature = primitives::sign::sign_eip712_message(
        "Uniswap V2",
        "1",
        1,
        address!("B4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"),
        "test",
        config.caller,
        address!("B4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"),
        U256::from(100),
        U256::from(0),
        U256::from(0),
        config,
    )
    .await?;

    println!("{:?}", signature);

    Ok(())
}
