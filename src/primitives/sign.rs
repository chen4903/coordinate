#![allow(missing_docs)]

use crate::config::Config;
use alloy::{
    signers::{local::PrivateKeySigner, Signer},
    sol,
    sol_types::{eip712_domain, SolStruct},
};
use alloy_primitives::{keccak256, Address, Signature, U256};
use serde::Serialize;
use std::{error::Error, str::FromStr};

pub async fn sign_message(content: String, config: Config) -> Result<Signature, Box<dyn Error>> {
    let private_key = config.private_key;

    let signer = PrivateKeySigner::from_str(&private_key).unwrap();
    let signer = signer.with_chain_id(Some(config.chain_id));

    let message = content.as_bytes();
    let signature = signer.sign_message(message).await?;

    Ok(signature)
}

sol! {
    #[derive(Serialize)]
    struct Permit {
        address owner;
        address spender;
        uint256 value;
        uint256 nonce;
        uint256 deadline;
    }
}

pub async fn sign_eip712_message(
    domain_name: &str,
    domain_version: &str,
    domain_chain_id: u64,
    domain_verifying_contract: Address,
    domain_salt: &str,
    permit_owner: Address,
    permit_spender: Address,
    permit_value: U256,
    permit_nonce: U256,
    permit_deadline: U256,
    config: Config,
) -> Result<Signature, Box<dyn Error>> {
    let private_key = config.private_key;
    let signer = PrivateKeySigner::from_str(&private_key).unwrap();

    let domain = eip712_domain! {
        name: domain_name.to_string(),
        version: domain_version.to_string(),
        chain_id: domain_chain_id,
        verifying_contract: domain_verifying_contract,
        salt: keccak256(domain_salt.to_string()),
    };

    let permit = Permit {
        owner: permit_owner,
        spender: permit_spender,
        value: permit_value,
        nonce: permit_nonce,
        deadline: permit_deadline,
    };

    let hash = permit.eip712_signing_hash(&domain);
    let signature = signer.sign_hash(&hash).await?;

    Ok(signature)
}
