pragma solidity 0.8.0;

library solidityLib{
    // 用法： solidityLib.strConcat("hello","hello");

    // 判断是不是偶数(奇数)
    function isEven(uint256 _number) public pure returns(bool){
        return _number & uint256(1) == 0;
    }

    // 字符串拼接
    function strConcat(string memory _a, string memory _b) external pure returns (string memory) {
        bytes memory _ba = bytes(_a);
        bytes memory _bb = bytes(_b);
        string memory ret = new string(_ba.length + _bb.length);
        bytes memory bret = bytes(ret);
        uint256 k = 0;
        for (uint256 i = 0; i < _ba.length; i++) bret[k++] = _ba[i];
        for (uint256 i = 0; i < _bb.length; i++) bret[k++] = _bb[i];
        return string(ret);
    }

    // uint转str
    function uintToStr(uint _i) external pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint j = _i;
        uint len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint k = len;
        while (_i != 0) {
            k = k-1;
            uint8 temp = (48 + uint8(_i - _i / 10 * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }

    // 发送原生的calldata
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
    
    // 用于链下获取CREATE2部署将会得到的地址
    function getProxyAddress(bytes32 salt, address implementation) public view returns (address proxy) {
        bytes memory code = abi.encodePacked(type(Proxy).creationCode, uint256(uint160(implementation)));
        bytes32 hash = keccak256(abi.encodePacked(bytes1(0xff), address(this), salt, keccak256(code)));
        proxy = address(uint160(uint256(hash)));
    }

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