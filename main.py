import re
import sys
import time
from rich import print
import PixivAPI


def new_file():
    PixivAPI.mkdir(PixivAPI.config.data("user", "save_file"))


def show_image_information(
        index: int, update: str, author_name: str,
        image_name: str, image_id: int, tags_llist: list
):
    print("\n第{}幅插图:".format(index))
    print("插画名称: {}:".format(image_name))
    print("插画ID: {}".format(image_id))
    print("作者名称: {}".format(author_name))
    print("插画标签: {}".format(', '.join(tags_llist)))
    print("发布时间: {}\n\n".format(update))


def shell_collection():
    response = PixivAPI.PixivApp.start_information()
    if type(response) is list or response == []:
        for index, values in enumerate(response):
            author_name = values.user['name']
            image_name = values.title
            image_id = values.id
            update = values.create_date
            tags_llist = [i['name'] for i in values['tags']]
            show_image_information(
                index, update, author_name, image_name, image_id, tags_llist
            )
            shell_illustration(image_id)


def shell_recommend(inputs):
    if len(inputs) >= 2:
        image_id = PixivAPI.rec_id(str(inputs[1]))
        response = PixivAPI.PixivApp.about_recommend(image_id)
    else:
        response = PixivAPI.PixivApp.recommend_information()
    if type(response) is list or len(response):
        PixivAPI.Download.threading_download(response)
    else:
        print(response)


def shell_illustration(inputs: list):
    start = time.time()
    if len(inputs) == 2:
        image_id = PixivAPI.rec_id(inputs[1])
        if type(image_id) is int and image_id != "":
            PixivAPI.Download.save_image(image_id)
        print(f'下载耗时:{round(time.time() - start, 2)} 秒')
    if len(inputs) == 3 and inputs[2] == "all":
        response = PixivAPI.PixivApp.author_information(inputs[1])
        if type(response) is list and len(response) != 0:
            PixivAPI.Download.threading_download(response)
            print(f'下载耗时:{round(time.time() - start, 2)} 秒')
        else:
            print(response)
    else:
        print("你没有输入id或者链接")


def shell_search(png_name: str, target='partial_match_for_tags'):
    response = PixivAPI.PixivApp.search_information(png_name, target)
    if type(response) is list or response == []:
        for search_data in response:
            image_id = search_data['id']
            image_name = PixivAPI.remove_str(search_data['title'])
            shell_illustration(image_id)


def shell_pixiv_token():
    for retry in range(int(PixivAPI.config.data("headers", "retry"))):
        if PixivAPI.config.data("user", "access_token") != "":
            return True
        print("本地配置文件没有令牌，请登入网站获取code")
        PixivAPI.login_pixiv.login()


def shell():
    if len(sys.argv) > 1 and type(sys.argv) is list:
        command_line = True
        inputs = sys.argv[1:]
    else:
        command_line = False
        print(PixivAPI.config.data("user", "help"))
        inputs = re.split('\\s+', PixivAPI.input_('>').strip())
    while True:
        if inputs[0] == 'q' or inputs[0] == 'quit':
            sys.exit("已退出程序")
        elif inputs[0] == 'h' or inputs[0] == 'help':
            print(PixivAPI.config.data("user", "help"))
        elif inputs[0] == 'd' or inputs[0] == 'download':
            shell_illustration(inputs)
        elif inputs[0] == 's' or inputs[0] == 'stars':
            shell_collection()
        elif inputs[0] == 'n' or inputs[0] == 'name':
            shell_search(inputs[1])
        elif inputs[0] == 't' or inputs[0] == 'recommend':
            shell_recommend(inputs)
        elif inputs[0] == 'f' or inputs[0] == 'follow':
            response = PixivAPI.PixivApp.follow_information()
            print(response)
        else:
            print(inputs[0], "为无效指令")
        if command_line is True:
            sys.exit(1)
        inputs = re.split('\\s+', PixivAPI.input_('>').strip())


if __name__ == '__main__':
    shell_pixiv_token()
    new_file()
    shell()
