// SPDX-License-Identifier: GPL-3.0
// 用于获得某个合约的runtimecode

pragma solidity 0.8.23;

contract GetRuntimeCode {
    function getAddressCode(address _target) public view returns (bytes memory code) {
        uint size;
        assembly {
            size := extcodesize(_target)
            code := mload(0x40)
            mstore(0x40, add(code, and(add(add(size, 0x20), 0x1f), not(0x1f))))
            mstore(code, size)
            extcodecopy(_target, add(code, 0x20), 0, size)
        }
    }
}