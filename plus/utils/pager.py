# -*- coding:utf8 -*-
class Pager():
    def __init__(self, current_page, all_counts, params_dict, base_url, per_page=1, show_page=11):
        '''
        生成分页按钮，返回起始索引和结束索引
        :param current_page: 当前页，即将要跳转的页码
        :param all_counts: 总数据量
        :param per_page: 一页显示多少数据
        :param show_page: 显示多少页
        :param base_url: 跳转的URL地址
        :param params_str: url里带的参数
        '''
        try:
            self.current_page = int(current_page)
            if self.current_page < 0:
                self.current_page = 1
        except Exception as e:
            self.current_page = 1

        self.all_counts = all_counts
        self.per_page = per_page
        self.show_page = show_page
        self.base_url = base_url
        a, b = divmod(self.all_counts, self.per_page)
        self.all_pages = a if not b else a + 1

        self.params_dict = params_dict

    @property
    def start_index(self):
        return (self.current_page - 1) * self.per_page

    @property
    def stop_index(self):
        return self.current_page * self.per_page

    def pager(self):
        # 确定选中页的位置
        half = int((self.show_page - 1) / 2)

        if self.all_pages < self.show_page:
            # 如果总页数小于设置的要显示的最大页数
            begin = 1
            end = self.all_pages + 1
        else:
            # 假如half=5，如果当前页面小于5的时候，那页面区间永远是1，11
            if self.current_page <= half:
                # 如果
                begin = 1
                end = self.show_page + 1
            elif self.current_page + half >= self.all_pages:
                # 假如half=5，如果当前页面加上5比总页数大，说明，这是最后一排页码标签
                begin = self.all_pages - self.show_page + 1
                end = self.all_pages + 1
            else:
                begin = self.current_page - half
                end = self.current_page + half + 1

        # 存放页码的集合，字符串
        page_list = []
        # 添加上一页按钮
        if self.current_page <= 1:
            prev = "<li class='disabled'><a>上一页</a></li>"
        else:
            self.params_dict["page"] = self.current_page - 1
            prev = "<li><a href='%s?%s'>上一页</a></li>" % (self.base_url, self.params_dict.urlencode(),)
        page_list.append(prev)

        # 添加分页标签
        for i in range(begin, end):
            self.params_dict["page"] = i
            if i == self.current_page:
                temp = "<li class='active'><a  href='%s?%s'>%s</a></li>" % (
                    self.base_url, self.params_dict.urlencode(), i,)
            else:
                temp = "<li><a href='%s?%s'>%s</a></li>" % (self.base_url, self.params_dict.urlencode(), i,)
            page_list.append(temp)

        if self.current_page >= self.all_pages:
            nex = "<li class='disabled' ><a>下一页</a></li>"
        else:
            self.params_dict["page"] = self.current_page + 1
            nex = "<li><a href='%s?%s'>下一页</a></li>" % (self.base_url, self.params_dict.urlencode(),)
        page_list.append(nex)

        return ''.join(page_list)
