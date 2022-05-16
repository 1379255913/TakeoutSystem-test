import pytest
import requests
from session import session1,session2,session3,url_headers



class TestSession:
    def my_fav(self,session):
        rps = session().get(url_headers+'/my_fav')
        return rps.text

    def test_01(self):
        assert self.my_fav(session1)=='我的收藏页面'

    def test_02(self):
        assert self.my_fav(session2)=='我的收藏页面'

    def test_03(self):
        assert self.my_fav(session3)=='我的收藏页面'

if __name__ == '__main__':
    pytest.main(['-vs','test_session.py'])
