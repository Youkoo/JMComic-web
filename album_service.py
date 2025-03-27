import gc
import re # 导入 re 模块
from pathlib import Path
import os  # 导入 os 模块

from jmcomic import download_album
# 假设 JmOption 是配置类，虽然这里没直接用，但 opt 参数可能就是这个类型
# from jmcomic import JmOption

from pdf_util import merge_webp_to_pdf


def sanitize_filename(filename):
    """移除或替换 Windows/Linux 文件名中的非法字符。"""
    # 移除 Windows 中的非法字符: < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除开头和结尾的空白字符
    sanitized = sanitized.strip()
    # Windows 文件名不能以句点或空格结尾
    sanitized = sanitized.rstrip('. ')
    # 将多个连续的下划线替换为单个下划线
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized


def get_album_pdf_path(jm_album_id, pdf_dir, is_pwd, opt):
    """
    下载 JMComic 漫画并转换为 PDF，实现缓存机制。

    Args:
        jm_album_id: 要下载的漫画 ID。
        pdf_dir: 保存最终 PDF 文件的目录。
        is_pwd: 布尔值，指示 PDF 是否应受密码保护。
        opt: 用于 download_album 的 JmOption 对象或类似配置。

    Returns:
        生成或已存在的 PDF 文件的路径。

    缓存行为:
    1. 函数首先调用 `download_album` 来获取漫画元数据（如标题）并下载图片。
       假设 `download_album` 可能内部实现了避免重复下载已存在图片文件夹的机制。
    2. 然后根据漫画标题构建预期的 PDF 文件路径。
    3. 如果该路径下已存在 PDF 文件，则跳过 PDF 生成步骤，直接返回现有路径（缓存命中）。
    4. 如果 PDF 不存在，则继续从下载的图片（预期在 `./{album.title}` 文件夹中）生成 PDF。
    """
    # 确保 pdf_dir 存在
    Path(pdf_dir).mkdir(parents=True, exist_ok=True)

    # 步骤 1: 构建基于 ID 的 PDF 文件路径
    pdf_filename = f"{jm_album_id}.pdf" # 使用 ID 命名
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    # 步骤 2: 检查 PDF 是否已存在 (缓存命中)
    if os.path.exists(pdf_path):
        print(f"PDF 文件已存在 (缓存命中): {pdf_path}")
        return pdf_path

    # PDF 不存在，继续下载和生成
    print(f"开始处理漫画 ID: {jm_album_id}，将生成 PDF: {pdf_path}")
    try:
        # 步骤 3: 下载漫画（获取元数据和图片）
        # download_album 内部应处理图片是否已存在的问题
        album, _ = download_album(jm_album_id, option=opt)
        print(f"漫画 '{album.title}' 元数据获取/下载初步完成。")
    except Exception as e:
        print(f"错误：下载或获取漫画 {jm_album_id} 元数据失败: {e}")
        raise # 如果下载失败，则向上抛出异常

    # 步骤 4: 生成 PDF
    # 清理 album.title 以匹配实际下载时创建的文件夹名称
    webp_folder_name = sanitize_filename(album.title)
    webp_folder_path = Path(webp_folder_name) # 相对于当前工作目录

    # 在尝试合并之前，检查源图片文件夹是否存在
    if not webp_folder_path.is_dir():
        print(f"错误：找不到用于生成 PDF 的图片文件夹: {webp_folder_path.absolute()}")
        # 处理此错误 - 下载可能失败或文件放在了别处？
        raise FileNotFoundError(f"图片文件夹 '{webp_folder_path}' 在尝试下载后未找到。")

    try:
        print(f"开始从 '{webp_folder_path}' 合并生成 PDF: {pdf_path}")
        # 根据 is_pwd 决定是否传递密码以及密码内容
        password_to_set = str(jm_album_id) if is_pwd else None
        merge_webp_to_pdf(str(webp_folder_path), pdf_path=pdf_path, is_pwd=is_pwd, password=password_to_set)
        print(f"成功生成 PDF: {pdf_path}")
        gc.collect()
    except Exception as e:
        print(f"错误：为漫画 {jm_album_id} ('{album.title}') 生成 PDF 时出错: {e}")
        # 清理可能不完整的 PDF 文件？
        if Path(pdf_path).exists():
            try:
                os.remove(pdf_path)
                print(f"已删除可能不完整的 PDF: {pdf_path}")
            except OSError as rm_err:
                print(f"错误：删除不完整的 PDF {pdf_path} 时出错: {rm_err}")
        raise # 重新引发 PDF 生成错误

    return pdf_path
