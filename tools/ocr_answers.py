# -*- coding: utf-8 -*-
"""对扫描版答案 PDF 做 OCR，输出文本缓存文件。"""
import sys
import os
import numpy as np
import pypdfium2 as pdfium
from rapidocr_onnxruntime import RapidOCR


def ocr_pdf(pdf_path, out_path):
    engine = RapidOCR()
    pdf = pdfium.PdfDocument(pdf_path)
    out_lines = []
    total = len(pdf)
    for i in range(total):
        page = pdf[i]
        bitmap = page.render(scale=2.2)
        pil = bitmap.to_pil()
        arr = np.array(pil.convert('RGB'))
        result, _ = engine(arr)
        page_lines = []
        if result:
            for box, text, conf in result:
                page_lines.append(str(text))
        out_lines.append('==PAGE %d==' % (i + 1))
        out_lines.extend(page_lines)
        print('page', i + 1, '/', total, 'lines:', len(page_lines), flush=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))
    print('saved', out_path)


if __name__ == '__main__':
    ocr_pdf(sys.argv[1], sys.argv[2])
