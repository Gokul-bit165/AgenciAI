try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

class OCRAgent:
    def __init__(self):
        if PaddleOCR:
            # use_angle_cls=True for better accuracy on scanned docs
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        else:
            self.ocr = None
            print("Warning: PaddleOCR not installed. OCR will fail.")

    def extract_text(self, image_path: str):
        if not self.ocr:
            return "Error: OCR not available"
        
        try:
            result = self.ocr.ocr(image_path, cls=True)
            text_lines = []
            if result and result[0]:
                for line in result[0]:
                    # line format: [[coords], [text, confidence]]
                    text_lines.append(line[1][0])
            return "\n".join(text_lines)
        except Exception as e:
            return f"OCR Processing Error: {str(e)}"
