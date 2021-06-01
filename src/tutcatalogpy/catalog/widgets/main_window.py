from tutcatalogpy.common.files import relative_path
from tutcatalogpy.common.widgets.main_window import CommonMainWindow


class MainWindow(CommonMainWindow):
    WINDOW_TITLE = 'TutCatalogPy2 Catalog'
    WINDOW_ICON_FILE = relative_path(__file__, '../../resources/icons/catalog.png')
