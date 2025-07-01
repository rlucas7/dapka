from collections2.add import add

import pytest

# uncomment if needed
#from unittest import TestCase



class TestAdd:
    # you can use the parametrize fixture for concise looping like so
    @pytest.mark.parametrize("a,b,expected", [(3,5,8), (2,4,6)])
    def test_add(self, a, b, expected):
        assert add(a, b) == expected

