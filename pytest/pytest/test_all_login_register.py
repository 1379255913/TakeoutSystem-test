import pytest
import requests
from session import session1,session2,session3,url_headers,session4,session5

class TestLogin:
    def login(self,email,password):
        data = {'email': email, 'password': password}
        ans = requests.post(url_headers + '/login', data=data)
        return ans.text

    def test_01_(self):
        assert self.login('1379255913@qq.com', '123456') == "登录用户页面"

    def test_02_(self):
        assert self.login('admin@qq.com', '123456') == "登录后台页面"

    def test_03_(self):
        assert self.login('1379255913@qq.com', '1234567') == "密码错误"

    def test_04_(self):
        assert self.login('1379255913@qq.com', '') == "请将信息填写完整"

    def test_05_(self):
        assert self.login('vvv@qq.com', '1234') == "该用户不存在"


class TestRegister:
    def register(self,email,nickname,password_1,password_2,phone,address,type1) ->str:
        data = {'email': email,'nickname':nickname,'password_1':password_1,'password_2':password_2,'phone':phone,'address':address,'type1':type1}
        ans = requests.post(url_headers + '/register', data=data)
        return ans.text

    def test_01_(self):
        assert self.register('1379255913@qq.com','gl','123456','123456','123456','123','0')=='该用户名已存在'

    def test_02_(self):
        assert self.register('1379255913@qq.com','gl','','123456','123456','123','0')=="信息填写不全，请将信息填写完整"

    def test_03_(self):
        assert self.register('test3@qq.com','gl','1234567','123456','123456','123','0')=="两次密码填写不一致"

    # def test_04_(self):
    #     assert self.register('test3@qq.com','gl','123456','123456','123456','123','0')=="注册成功"




class TestChangeInfo:
    def changeinfo_post(self,session,new_nickname,new_phone,new_address,new_info,new_photo,new_tags):
        if new_photo:
            with open(new_photo, 'rb') as f:
                files={'new_photo':f}
                data={'new_nickname':new_nickname,'new_phone':new_phone,'new_address':new_address,'new_info':new_info,'tags':new_tags}
                ans = session().post(url_headers + '/change_info', data=data,files=files)
        else:
            data = {'new_nickname': new_nickname, 'new_phone': new_phone, 'new_address': new_address,
                    'new_info': new_info, 'tags': new_tags}
            ans = session().post(url_headers + '/change_info', data=data)
        return ans.text

    def test_01_(self):
        assert self.changeinfo_post(session4,'test','12345678','aoe','aoe1','test1.jpg',"") == "修改个人信息成功照片"

    def test_02_(self):
        assert self.changeinfo_post(session4, 'test', '12345678', 'aoe', 'aoe1', '', "") == "修改个人信息成功"

    def test_03_(self):
        assert self.changeinfo_post(session4, 'test', '', 'aoe', 'aoe1', '', "") == "信息填写不全"

    def test_04_(self):
        assert self.changeinfo_post(session5, 'test2', '12345678', 'test2', 'test2', '', "") == "修改个人信息成功"

    def test_05_(self):
        assert self.changeinfo_post(session5, 'test2', '12345678', 'test2', 'test2', '', "早餐")=='修改个人信息成功标签'

    def test_06_(self):
        assert self.changeinfo_post(session5, 'test2', '12345678', 'test2', 'test2', 'test1.jpg', "早餐") == "修改个人信息成功照片标签"

    def test_07_(self):
        assert self.changeinfo_post(session5, 'test2', '12345678', 'test2', 'test2', 'test2.png', "早餐") == "上传照片格式错误"


class TestChangePassword:
    def change_password_post(self,session,old_password,new_password1,new_password2):
        data={'old_password':old_password,'new_password1':new_password1,'new_password2':new_password2}
        ans = session().post(url_headers + '/change_password', data=data)
        return ans.text

    def test_01_(self):
        assert self.change_password_post(session4,'123456','123456','123456')=="修改密码成功"

    def test_02_(self):
        assert self.change_password_post(session4,'','','123456')=="信息填写不全"

    def test_03_(self):
        assert self.change_password_post(session4,'123456','123456','1234w56')=="两次新密码不一致"

    def test_04_(self):
        assert self.change_password_post(session4,'1234567','123456','123456')=="旧密码错误"


class TestCreateFood:
    def create_food_post(self,session,new_name,new_price,new_info,new_photo,new_movie,type1):
        f1=None
        f2=None
        files = {}
        if new_photo:
            f1=open(new_photo,'rb')
            files['new_photo']=f1
        if new_movie:
            f2=open(new_movie,'rb')
            files['new_movie']=f2
        data={'new_name':new_name,'new_price':new_price,'new_info':new_info,'type1':type1}
        ans = session().post(url_headers + '/create_food', data=data, files=files)
        if f1:f1.close()
        if f2:f2.close()
        return ans.text

    def test_01_(self):
        assert self.create_food_post(session5,"测试菜品","13.03522","test","test1.jpg","test.mp4","0")=="添加商品成功"

    def test_02_(self):
        assert self.create_food_post(session5,"测试菜品","13.5","test","test1.jpg","","0")=="添加商品成功"

    def test_03_(self):
        assert self.create_food_post(session5,"测试菜品","fe","test","test1.jpg","","0")=="商品价格错误"

    def test_04_(self):
        assert self.create_food_post(session5,"测试菜品","13.5","test","","","0")=="信息填写不全"

    def test_05_(self):
        assert self.create_food_post(session5,"测试菜品","13.5","test","test2.png","","0")=="上传照片格式错误"

    def test_06_(self):
        assert self.create_food_post(session5,"测试菜品","","","test1.jpg","","0")=="信息填写不全"

    def test_07_(self):
        assert self.create_food_post(session5,"测试菜品","13.5","test","test1.jpg","test1.jpg","0")=="上传视频格式错误"




class TestChangeType:
    def change_type_post(self,session,type0,type1,type2,type3,type4,type5,type6,type7,type8,type9):
        data={'type0':type0,'type1':type1,'type2':type2,'type3':type3,'type4':type4,'type5':type5,'type6':type6,'type7':type7,'type8':type8,'type9':type9,}
        ans = session().post(url_headers + '/change_type', data=data)
        return ans.text

    def test_01_(self):
        assert self.change_type_post(session5,'test1','test2','test3','test4','test5','test6','test7','','','')=="编辑菜品类型成功"

    def test_02_(self):
        assert self.change_type_post(session5, 'test1', 'test1', 'test1', 'test1', 'test1', 'test1', 'test1', '', '',
                                     '') == "编辑菜品类型成功"

    def test_03_(self):
        assert self.change_type_post(session5,'','','','','','','','', '', '') == "编辑菜品类型成功"


class TestEmailConfirm:
    def email_confirm_post(self,session,the_email,confirm,new_password,getid):
        data={"the_email":the_email,"confirm":confirm,"new_password":new_password,"getid":getid}
        ans = session().post(url_headers + '/email_confirm', data=data)
        return ans.text

    def test_01_(self):
        assert self.email_confirm_post(session4,"test2@qq.com","b6608d","123456","FEVDRMBYXY")=="修改密码成功"

    def test_02_(self):
        assert self.email_confirm_post(session4,"test2@qq.com","b6608d","","FEVDRMBYXY")=="请将信息填写完整"

    def test_03_(self):
        assert self.email_confirm_post(session4,"test2@qq.com","b66082","123456","FEVDRMBYXY")=="验证码错误"



class TestShopDetail:
    def shop_detail_post(self,session,result,Ino):
        data={"result":result}
        ans = session().post(url_headers + '/shop_detail/'+Ino, data=data)
        return ans.text

    def test_01_(self):
        assert self.shop_detail_post(session5,"39","test2@qq.com")=="删除成功"



class TestPostIssue:
    def post_issue_post(self,session,title,editorValue,shop):
        data={'title':title,'editorValue':editorValue}
        ans = session().post(url_headers + '/post_issue/' + shop, data=data)
        return ans.text

    def test_01_(self):
        assert self.post_issue_post(session4,"测试","<h1>test</h1>",'test2@qq.com')=="发表评论成功"

    def test_02_(self):
        assert self.post_issue_post(session4,"测试","",'test2@qq.com')=="发表评论成功"

    def test_03_(self):
        assert self.post_issue_post(session4,"","<h1>test</h1>",'test2@qq.com')=="发表评论成功"





class TestOrder:
    def order(self,session,result,Ino):
        data={'result':result}
        ans = session().post(url_headers + '/order/' + Ino, data=data)
        return ans.text

    def test_01_(self):
        assert self.order(session4,'黄金鸡块/13.5/1%薯条/11/1%27.5','test2@qq.com')=="点餐完成"




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






if __name__ == '__main__':
    pytest.main(['-vs','test_all_login_register.py::TestRegister'])