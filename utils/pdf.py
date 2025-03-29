from pathlib import Path

from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

# 将指定文件夹下的所有 .webp 文件按照文件名顺序合并为 PDF 长图，并可选加密。
# @param folder_path: 包含 .webp 文件的文件夹路径
# @param pdf_path: 输出文件夹
# @param is_pwd: 是否加密 PDF 文件

# @TR0MXI
def merge_webp_to_pdf(folder_path, pdf_path, password=None):
    """
    将指定文件夹下的所有 .webp 文件按照文件名顺序合并为 PDF 长图，并可选加密。

    :param folder_path: 包含 .webp 文件的文件夹路径
    :param pdf_path: 输出文件夹
    :param is_pwd: 输出 PDF 文件的路径
    :param password: PDF 文件的密码（可选）
    """
    output_dir = Path(pdf_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    webp_files = sorted(Path(folder_path).glob("*.webp"))

    if not webp_files:
        raise FileNotFoundError(f"文件夹 {folder_path} 中没有找到 .webp 文件")

    images = [Image.open(webp).convert("RGB") for webp in webp_files]

    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    for image in images:
        image.close()
    del images

    print(f"PDF 文件已生成：{pdf_path}")

    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()

    for page in pdf_reader.pages:  
        page.compress_content_streams()
        pdf_writer.add_page(page)

    if password:
        pdf_writer.encrypt(password)
        print(f"PDF 文件已加密：{pdf_path}")

    with open(pdf_path, "wb") as f:
        pdf_writer.write(f)
