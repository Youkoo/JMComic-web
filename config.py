class config:
    host = '0.0.0.0'
    port = 8699
    option_file = './option.yml'
    pdf_dir = './pdf'
    pdf_pwd = True
    # 原作者也用配置文件，为了简易性，还是跟随原作者设计吧，废弃这个配置
    # jmOpt = { #直接用字典存取配置，减少文件io
    #     "log": True,

    #     "plugins": {
    #         "after_album": [
    #             {
    #                 "plugin": "img2pdf",
    #                 "kwargs": {
    #                     "pdf_dir": "./pdf",
    #                     "filename_rule": "Aname"  # pdf 命名规则，A 代表 album, name 代表使用 album.name 也就是本子名称
    #                 }
    #             }
    #         ]
    #     }
    # }
