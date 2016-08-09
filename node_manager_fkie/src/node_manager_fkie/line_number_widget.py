from python_qt_binding.QtCore import Qt
from python_qt_binding.QtGui import QPainter
try:
    from python_qt_binding.QtGui import QWidget, QFrame, QHBoxLayout
except:
    from python_qt_binding.QtWidgets import QWidget, QFrame, QHBoxLayout


class LineNumberWidget(QFrame):

    class NumberBar(QWidget):

        def __init__(self, *args):
            QWidget.__init__(self, *args)
            self.edit = None
            # it is the highest line that is currently visible.
            self.highest_line = 0

        def set_text_edit(self, edit):
            self.edit = edit

        def update(self, *args):
            # the +4 is used to compensate for the current line being bold.
            width = self.fontMetrics().width(str(self.highest_line)) + 4
            if self.width() != width:
                self.setFixedWidth(width)
            QWidget.update(self, *args)

        def paintEvent(self, event):
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())
            painter = QPainter(self)
            painter.setPen(Qt.darkGray)
            line_count = 0
            # Iterate over all text blocks in the document.
            block = self.edit.document().begin()
            while block.isValid():
                line_count += 1
                # the top left position of the block in the document
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
                # check if the position of the block is out side of visible area
                if position.y() > page_bottom:
                    break
                # we want the line number for the selected line to be bold.
                bold = False
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                    painter.setPen(Qt.black)
                # Draw the line number right justified at the y position of the
                # line. 3 is the magic padding number. drawText(x, y, text)
                painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3, round(position.y()) - contents_y + font_metrics.ascent() + self.edit.document().documentMargin(), str(line_count))
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
                    painter.setPen(Qt.darkGray)

                block = block.next()

            self.highest_line = line_count
            painter.end()
            QWidget.paintEvent(self, event)

    def __init__(self, editor, *args):
        QFrame.__init__(self, *args)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.edit = editor

        self.number_bar = self.NumberBar()
        self.number_bar.set_text_edit(self.edit)

        hbox = QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary signals.
        if obj in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QFrame.eventFilter(obj, event)

    def get_text_edit(self):
        return self.edit
