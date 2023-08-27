# This is a sample Python script.
import io
import os.path

import PyPDF2
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def unify_page_frame(in_fp, out_dir, padding: int = 0, show_progress: bool = True):
    in_fn = os.path.basename(in_fp)
    pdf_fn_without_extension = os.path.splitext(in_fn)[0]
    out_fp = os.path.join(out_dir, in_fn)
    with open(in_fp, 'rb') as f:
        reader = PdfReader(f)
        writer = PdfWriter()
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            xObject = page['/Resources']['/XObject'].get_object()
            img_fn_without_extension = f"{pdf_fn_without_extension}_{page_num}"
            img_fn = None
            img_fp = None
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    data = xObject[obj].get_data()
                    if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                        mode = "RGB"
                    else:
                        mode = "P"
                    if xObject[obj]['/Filter'] == '/FlateDecode':
                        img_fn = img_fn_without_extension + ".png"
                        img_fp = os.path.join("imgs", img_fn)
                        img = Image.frombytes(mode, size, data)
                        img.save(img_fp)
                    elif xObject[obj]['/Filter'] == '/DCTDecode':
                        img_fn = img_fn_without_extension + ".jpg"
                        img_fp = os.path.join("imgs", img_fn)
                        img = open(img_fp, "wb")
                        img.write(data)
                        img.close()
                    elif xObject[obj]['/Filter'] == '/JPXDecode':
                        img_fn = img_fn_without_extension + ".jp2"
                        img_fp = os.path.join("imgs", img_fn)
                        img = open(img_fp, "wb")
                        img.write(data)
                        img.close()
            img = ImageReader(img_fp)
            # 获取图片的宽度和高度
            img_width, img_height = img.getSize()
            # 创建一个新的 PDF 页面对象
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            c.drawImage(img_fp, 0 + padding, 0 + padding, width=612 - padding * 2, height=792 - padding * 2)
            c.save()

            # 移动到开始，并创建一个新的 PDF 页面对象
            packet.seek(0)
            new_pdf = PyPDF2.PdfReader(packet)

            # 获取新的 PDF 页面
            new_page = new_pdf.pages[0]
            if show_progress:
                print(f"{(page_num + 1) / len(reader.pages) * 100:.2f}%", f"第{page_num + 1}/{len(reader.pages)}页",
                      page.mediabox,
                      "=" * 10,
                      (img_width, img_height), "=" * 10, ">>>", new_page.mediabox)
            # 将新的页面添加到 PDF 写入对象中
            writer.add_page(new_page)
            # new_page = PyPDF2.PageObject.create_blank_page(width=w, height=h)
        with open(out_fp, 'wb') as wf:
            writer.write(wf)


def bulk_unify_page_frame(source_dir, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    fns = os.listdir(source_dir)
    for fn in fns:
        if not fn.endswith(".pdf"):
            continue
        fp = os.path.join(source_dir, fn)
        print(fp, end='')
        unify_page_frame(fp, target_dir, show_progress=False)
        print("(Done!)")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bulk_unify_page_frame("新建文件夹", "out")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
