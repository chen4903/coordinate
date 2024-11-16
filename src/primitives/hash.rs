use alloy::primitives::{eip191_hash_message, keccak256 as alloy_keccak256, Bytes, FixedBytes};

pub fn keccak256(content: Bytes) -> FixedBytes<32> {
    alloy_keccak256(content)
}

pub fn eip191_hash(content: Bytes) -> FixedBytes<32> {
    // `"\x19Ethereum Signed Message:\n" + message.length + message`
    eip191_hash_message(content)
}
