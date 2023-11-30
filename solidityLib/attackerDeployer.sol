pragma solidity 0.8.0;

// CREATE2部署特殊的攻击合约
contract DeployAttacker {
    bytes attackCode =hex"00"; // initcode

    function deploy(bytes32 salt) public {
        bytes memory bytecode = attackCode;
        address addr;
        assembly {
        	addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        }
    }
    function getHash()public view returns(bytes32){
        return keccak256(attackCode);
    }
}