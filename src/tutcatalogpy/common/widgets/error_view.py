from typing import Optional

from tutcatalogpy.common.widgets.growing_text_edit import GrowingTextEdit


class ErrorView(GrowingTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFrameShape(ErrorView.NoFrame)
        self.viewport().setAutoFillBackground(False)

    def set_error(self, text: Optional[str]) -> None:
        if text is None:
            self.clear()
        else:
            header, body = text.split('\n', 1)
            self.setText(f'<h1>{header}</h1>{body}')


if __name__ == '__main__':
    from tutcatalogpy.catalog.main import run
    run()
