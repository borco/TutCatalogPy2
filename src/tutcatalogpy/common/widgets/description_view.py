import logging
from pathlib import Path
from typing import Dict, Final, Optional

from markdown import Markdown
from markdown.extensions import (
    admonition,
    fenced_code,
    nl2br,
    sane_lists,
    tables,
)
from PySide2.QtCore import QUrl, Qt
from PySide2.QtWidgets import QFrame

from tutcatalogpy.common.widgets.growing_text_edit import GrowingTextEdit

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

DESCRIPTION_STYLE_SHEET_ARGS: Final[Dict] = {
    'pink': '#ffb3ba',
    'orange': '#ffdfba',
    'yellow': '#ffffba',
    'green': '#baffc9',
    'blue': '#bae1ff',
    'grey': '#d7d7d7',
    'h1-background': '#808080',
    'h2-background': '#909090',
    'h3-background': '#a0a0a0',
    'h4-background': '#b0b0b0',
    'h5-background': '#c0c0c0',
    'h6-background': '#d0d0d0',
    'h1-color': '#f0f0f0',
    'h2-color': '#f0f0f0',
    'h3-color': '#f0f0f0',
    'h4-color': '#404040',
    'h5-color': '#404040',
    'h6-color': '#404040',
    'h1-font-weight': '900',
    'h2-font-weight': '900',
    'h3-font-weight': '900',
    'h4-font-weight': '900',
    'h5-font-weight': '900',
    'h6-font-weight': '500',
    'admonition-margin-left': '10px',
    'pre-margin-left': '10px',
    'code-color': '#006000',
    'th-background': '#404040',
    'th-color': '#e0e0e0',
    'td-background': '#e0e0e0',
}

DESCRIPTION_STYLE_SHEET: Final[str] = """
h1, h2, h3, h4, h5, h6 {{
    font-variant: small-caps;
}}

h1 {{
    font-size: x-large;
    font-weight: {h1-font-weight};
    color: {h1-color};
    background: {h1-background}
}}

h2 {{
    font-size: large;
    font-weight: {h2-font-weight};
    color: {h2-color};
    background: {h2-background}
}}

h3 {{
    font-size: medium;
    font-weight: {h3-font-weight};
    color: {h3-color};
    background: {h3-background}
}}

h4 {{
    font-size: small;
    font-weight: {h4-font-weight};
    color: {h4-color};
    background: {h4-background}
}}

h5 {{
    font-size: small;
    font-weight: {h5-font-weight};
    color: {h5-color};
    background: {h5-background}
}}

h6 {{
    font-size: small;
    font-weight: {h6-font-weight};
    color: {h6-color};
    background: {h6-background}
}}

td, th {{
    padding: 2px;
}}

th {{
    background: {th-background};
    color: {th-color};
}}

td {{
    background: {td-background};
}}

.admonition {{
    margin-left: {admonition-margin-left};
}}

.admonition .admonition-title {{
    background: {grey};
    float: left;
}}

.note .admonition-title {{
    background: {blue};
}}

.warning .admonition-title {{
    background: {yellow};
}}

.error .admonition-title {{
    background: {pink};
}}

pre {{
    margin-left: {pre-margin-left};
}}

code {{
    color: {code-color};
}}
""".format(**DESCRIPTION_STYLE_SHEET_ARGS)


class DescriptionView(GrowingTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFrameShape(QFrame.NoFrame)
        self.viewport().setAutoFillBackground(False)
        self.setStyleSheet(DESCRIPTION_STYLE_SHEET)
        self.document().setDefaultStyleSheet(DESCRIPTION_STYLE_SHEET)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def set_content(self, description: str, path: Optional[Path] = None) -> None:
        base_url = QUrl(f'file://{path}/', QUrl.TolerantMode)
        md = Markdown(extensions=[
            admonition.AdmonitionExtension(),
            fenced_code.FencedCodeExtension(),
            nl2br.Nl2BrExtension(),
            sane_lists.SaneListExtension(),
            tables.TableExtension(),
        ])
        html = md.convert(description)
        document = self.document()
        document.setBaseUrl(base_url)
        document.setHtml(html)

        # log.raw_html(html)


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication, QScrollArea

    content = """
# H1 Title

## H2 Title

### H3 Title

#### H4 Title

##### H5 Title

###### H6 Title

---

*Bold*
**Italic**
***Bold & Italic***
<u>Underlined</u>

some `inline code` inside other text

* item 1
* item 2
* subitem 2.1
* subitme 2.2
    * subitem 2.2.1
    * subitem 2.2.2

1. item 1
1. item 2

## Admonition

!!! Note title
    Note text

!!! Warning title
    Warning text

!!! Error title
    Error text

!!! Generic title
    Generic text

## Fenced Code

```
# block code
ls -l
```

## nl2br

line 1
line 2

## Tables

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell
    """
    app = QApplication([])

    window = QScrollArea()
    view = DescriptionView()
    view.set_content(content)
    window.setWidget(view)
    window.resize(400, 900)
    window.show()

    app.exec_()
