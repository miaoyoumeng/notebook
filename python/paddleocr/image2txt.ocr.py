
import paddle
import paddleocr
from paddleocr import PaddleOCR

# paddle.utils.run_check()

print(__file__)

# # 初始化 PaddleOCR 实例
# print("ocr init....")
# ocr = PaddleOCR(
#     use_doc_orientation_classify = False,
#     use_doc_unwarping = False,
#     use_textline_orientation = False,
#     enable_mkldnn = True,
#     ocr_version = "PP-OCRv3",
#     cpu_threads = 4, 
#     lang = "ch")

# print("ocr init done....")
# # # 对示例图像执行 OCR 推理 
# input = "/Users/miaoyoumeng/screenshot/2026-02-07-21-50-32.png"
# result = ocr.predict(input)
# print("ocr predict done....")
# output = "/Users/miaoyoumeng/output.json"
# # 可视化结果并保存 json 结果
# for res in result:
#     # res.print()
# # #     # res.save_to_img("output")
#     res.save_to_json(output)
