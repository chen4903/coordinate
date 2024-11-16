use alloy::{
    network::{AnyNetwork, EthereumWallet},
    primitives::Address,
    providers::{
        fillers::{
            BlobGasFiller, ChainIdFiller, FillProvider, GasFiller, JoinFill, NonceFiller,
            WalletFiller,
        },
        Identity, Provider, ProviderBuilder, RootProvider,
    },
    signers::local::PrivateKeySigner,
    transports::http::{Client, Http},
};
use std::error::Error;

type ProviderType = FillProvider<
    JoinFill<
        JoinFill<
            Identity,
            JoinFill<GasFiller, JoinFill<BlobGasFiller, JoinFill<NonceFiller, ChainIdFiller>>>,
        >,
        WalletFiller<EthereumWallet>,
    >,
    RootProvider<Http<Client>, AnyNetwork>,
    Http<Client>,
    AnyNetwork,
>;

pub struct Config {
    pub private_key: String,
    pub caller: Address,
    pub etherscan_key: String,
    pub provider: ProviderType,
    pub chain_id: u64,
}

impl Config {
    pub async fn init(
        private_key: String,
        rpc_url: String,
        etherscan_key: String,
    ) -> Result<Self, Box<dyn Error>> {
        let signer: PrivateKeySigner = private_key.parse().map_err(|_| "Invalid private key")?;
        let wallet = EthereumWallet::from(signer);
        let address = wallet.default_signer().address();

        let provider = ProviderBuilder::new()
            .with_recommended_fillers()
            .network::<AnyNetwork>()
            .wallet(wallet.clone())
            .on_http(rpc_url.clone().parse()?);

        let chain_id = provider.get_chain_id().await?;

        Ok(Config {
            private_key,
            caller: address,
            etherscan_key,
            provider,
            chain_id,
        })
    }

    pub fn peek(self) -> Address {
        self.caller
    }
}
