// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.0;

// CREATE2部署特殊的攻击合约
// 需要注意gas，经常由于gas不足而部署失败
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

// 部署任意的runtimecode
contract Deployer {
    constructor(bytes memory code) {
        assembly {
            return (add(code, 0x20), mload(code))
        }
    }
}

contract stuff {
    // CREATE2部署相关
    function getHash(bytes memory bytecode)external pure returns(bytes32){
        return keccak256(bytecode);
    }

    function deploy_noConstructor(bytes32 salt) external returns(address) {
        bytes memory bytecode = hex"00";
        address addr;
        // 构造器没有参数
        assembly {
            addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        }
        return addr;
    }

    function deploy_constructor(address _addr01, address _addr02) external returns (address addr) {
        bytes memory bytecode = hex"00";
        // 构造器有2个参数：
        bytes memory bytecode_withConstructor = abi.encodePacked(bytecode, abi.encode(address(_addr01), address(_addr02)));
        assembly {
            addr := create(0, add(bytecode_withConstructor, 0x20), mload(bytecode_withConstructor))
        }
    }
}