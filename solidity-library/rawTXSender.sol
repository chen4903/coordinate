// SPDX-License-Identifier: GPL-3.0
// 发送原生的calldata
pragma solidity 0.8.23;

contract sender {
    
    function sendRawTx(address _addr) public {
        bytes memory data = abi.encodePacked(
            bytes4(0x4b2d25ef),
            bytes32(0x0000000000000000000000005695ef5f2e997b2e142b38837132a6c3ddc463b7),
            bytes32(0x00000000000000000000000000000000000000000001a784379d99db42000000),
            bytes32(0x0000000000000000000000000000000000000000000000000000000000002710)
        );
        uint size = data.length;
        address x = address(_addr);
        assembly{
            switch call(gas(), x, 0, add(data,0x20), size, 0, 0)
            case 0 {
                   returndatacopy(0x00,0x00,returndatasize())
                   revert(0, returndatasize())
            }
        }
    }
}