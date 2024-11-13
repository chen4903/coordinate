pub mod config;
pub mod contracts;
pub mod monitor;
pub mod signature;

use config::Config;

pub fn init(mode: String, private_key: String, rpc_url: String, etherscan_key: String) {
    let config = Config::new(mode, private_key, rpc_url, etherscan_key);

    // TODO: transfer config into each modules
}
