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

    let signature = primitives::sign::sign_message("hello".to_string(), config).await?;

    println!("{:?}", signature);

    Ok(())
}
