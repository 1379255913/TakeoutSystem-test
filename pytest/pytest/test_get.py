import pytest
import requests
from session import session1,session2,session3,url_headers,session4,session5





class TestGet:
    def index_get(self):
        ans = requests.get(url_headers + '/')
        return ans.text

    def test_01_(self):
        assert self.index_get()=="主页"

    def register_get(self):
        ans = requests.get(url_headers + '/register')
        return ans.text

    def test_02_(self):
        assert self.register_get()=="注册页面"

    def login_get(self):
        ans = requests.get(url_headers + '/login')
        return ans.text

    def test_03_(self):
        assert self.login_get()=="登录页面"

    def post_issue_get(self,session,shop):
        ans = session().get(url_headers + '/post_issue/'+shop)
        return ans.text

    def test_04_(self):
        assert self.post_issue_get(session4,"1234@qq.com")=="发布评论页面"

    def my_fav_get(self,session):
        ans = session().get(url_headers + '/my_fav')
        return ans.text

    def test_05_(self):
        assert self.my_fav_get(session4) == "我的收藏页面"


    def my_follow_get(self,session)->str:
        ans = session().get(url_headers + '/my_follow')
        return ans.text

    def test_06_(self):
        assert self.my_follow_get(session4) == "我的关注页面"


    def my_followed_get(self,session) ->str:
        ans = session().get(url_headers + '/my_followed')
        return ans.text


    def test_07_(self):
        assert self.my_followed_get(session4) == "我的粉丝页面"


    def shop_get(self) ->str:
        ans = requests.get(url_headers + '/shop')
        return ans.text

    def test_08_(self):
        assert self.shop_get() == "商家页面"

    def shop_detail_get(self,Ino) -> str:
        ans = requests.get(url_headers + '/shop_detail/'+Ino)
        return ans.text

    def test_09_(self):
        assert self.shop_detail_get("1234@qq.com") == "商家详情"


    def movie_get(self,Ino) -> str:
        ans = requests.get(url_headers + '/movie/'+Ino)
        return ans.text


    def test_10_(self):
        assert self.movie_get('2022030313092000.mp4') == "视频播放页面"

    def order_get(self,Ino) -> str:
        ans = requests.get(url_headers + '/order/'+Ino)
        return ans.text

    def orderdata_get(self,Ino) -> str:
        ans = requests.get(url_headers + '/orderdata/'+Ino)
        return ans.text

    def issue_get(self,Ino) -> str:
        ans = requests.get(url_headers + '/issue/'+Ino)
        return ans.text

    def personal_get(self,Ino) -> str:
        ans = requests.get(url_headers + '/personal/'+Ino)
        return ans.text

    def change_password_get(self) -> str:
        ans = requests.get(url_headers + '/change_password')
        return ans.text

    def change_info_get(self) -> str:
        ans = requests.get(url_headers + '/change_info')
        return ans.text

    def create_food_get(self) -> str:
        ans = requests.get(url_headers + '/create_food')
        return ans.text

    def change_type_get(self) -> str:
        ans = requests.get(url_headers + '/change_type')
        return ans.text

    def show_issue_get(self,Ino) -> str:
        ans = requests.get(url_headers + '/show_issue/'+Ino)
        return ans.text

    def search_ans_get(self,Ino,value) -> str:
        ans = requests.get(url_headers + '/search_ans/'+Ino+'/'+value)
        return ans.text



if __name__ == '__main__':
    pytest.main(['-vs','test_get.py'])