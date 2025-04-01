import tempfile
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image # Pillow for WebP to JPEG conversion
import gc

# WebP -> JPEG -> PyMuPDF 
# @TR0MXI 
# 换个PyMuPDF
def merge_webp_to_pdf(folder_path, pdf_path, password=None):
    """
    WebP 转 JPEG，然后使用 PyMuPDF 合并为 PDF 并可选加密 (极简版)。

    :param folder_path: 包含 .webp 文件的文件夹路径
    :param pdf_path: 输出 PDF 文件的路径
    :param password: PDF 文件的密码（可选）
    """
    folder_path = Path(folder_path)
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True) 

    webp_files = sorted(folder_path.rglob("*.webp"))
    if not webp_files:
        raise FileNotFoundError(f"No .webp files found in {folder_path}")

    doc = fitz.open()  

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for i, webp_file in enumerate(webp_files):
            try:
                img = Image.open(webp_file).convert("RGB")
                jpeg_path = temp_path / f"{i:04d}.jpg" 
                img.save(jpeg_path, "JPEG", quality=95)
                img.close()

                img_doc = fitz.open(str(jpeg_path))  
                doc.insert_pdf(img_doc)        
                img_doc.close()
            except Exception as e:
                 print(f"Skipping file {webp_file} due to error: {e}")
                 if 'img' in locals() and img: img.close() # 尝试关闭 Pillow Image
                 if 'img_doc' in locals() and img_doc: img_doc.close() 
                 continue

    save_opts = {"garbage": 4, "deflate": True}
    if password:
        save_opts.update({
            "encryption": fitz.PDF_ENCRYPT_AES_256,
            "owner_pw": password,
            "user_pw": password,
            "permissions": fitz.PDF_PERM_PRINT | fitz.PDF_PERM_COPY
        })

    if doc.page_count > 0: 
        doc.save(str(pdf_path), **save_opts)
        print(f"PDF generated: {pdf_path}{' (encrypted)' if password else ''}")
    else:
        print(f"Warning: No pages were successfully added to the PDF. Output file not created.")

    doc.close()
    gc.collect()
