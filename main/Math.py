"""
本模块用于解决常见的数学问题。
"""
import gmpy2
from functools import reduce

class Numbertheory():
    """
    本模块用于数论中出现的问题。
    """

    @staticmethod
    def CRT(moudle, a):
        """
        中国剩余定律/孙子定律

        参数：
            moudle: 模列表
            a: 同余值列表

        返回值：
            中国剩余定律结果

        例子：
            moudle = [3, 5, 7]
            a = [2, 4, 3]
            结果：59
        例子:
                require(_number % 0x3100e35e552c1273c959 == 0x2c2eb0597447608b329d);
                require(_number % 0x1ac3243c9e81ba850045 == 0x6369510a41dbcbed870);
                require(_number % 0x5ce6a91010e307946b87 == 0x301753fa0827117d1968);
            print(Numbertheory.CRT([0x3100e35e552c1273c959, 0x1ac3243c9e81ba850045, 0x5ce6a91010e307946b87],[0x2c2eb0597447608b329d, 0x6369510a41dbcbed870, 0x301753fa0827117d1968]))
        """
        M = reduce((lambda x, y : x * y), moudle)
        result = 0
        for mi in moudle:
            Mi = M // mi
            inv_Mi = gmpy2.invert(Mi, mi)
            result = (result + a[moudle.index(mi)] * Mi * inv_Mi) % M
        return result % M