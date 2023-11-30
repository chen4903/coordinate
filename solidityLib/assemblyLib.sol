pragma solidity 0.8.0;

library inlineLib{
    // 加法
    function add_unchecked(uint a, uint b) external pure returns (uint256) {
        assembly {
            mstore(0x0, add(a, b))
            return(0x0, 32)
        }
    }

    // 加法
    function add_checked(uint a, uint b) external pure returns (uint256) {
        assembly {
            let result := gt(add(a,b), b)
            if eq(result, 1){
                mstore(0x0, add(a, b))
                return(0x0, 32)
            }
            revert(0,0)
        }
        return 0; // 这个可以不用写
    }

    // 除法
    function divUint(uint a, uint b) external pure returns (uint256 q) {
        assembly {
            q := div(a, b)
        }
    }

    // 比较两个数字那个大
    function max(uint256 x, uint256 y) public pure returns (uint256 z) {
        /// @solidity memory-safe-assembly
        assembly {
            z := xor(x, mul(xor(x, y), gt(y, x)))
        }
    }//768

    // 判断是不是零地址
    function checkOptimized(address _caller) public pure returns (bool) {
        assembly {
            if iszero(_caller) {
                mstore(0x00, 0x20)
                mstore(0x20, 0x0c)
                mstore(0x40, 0x5a65726f20416464726573730000000000000000000000000000000000000000) // load hex of "Zero Address" to memory
                revert(0x00, 0x60)
            }
        }
        return true;
    }
}