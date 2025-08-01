# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_dataset.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(826, 461)
        Dialog.setStyleSheet(u"QWidget\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244);\n"
"    font: 16pt\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"    color: rgb(220, 130, 30);\n"
"}\n"
"\n"
"QLineEdit, QTextEdit, QTableWidget\n"
"{\n"
"   background-color:  rgb(245, 244, 244)\n"
"}\n"
"\n"
"QPushButton\n"
"{\n"
"	background-color: rgb(21, 165, 137);\n"
"    color: rgb(245, 244, 244);\n"
"}\n"
"\n"
"QPushButton#home_button, QPushButton#parent_button, QPushButton#refresh_button\n"
"{\n"
"    background-color: rgb(245, 244, 244);\n"
"}\n"
"\n"
"QTabWidget#info_tabs\n"
"{\n"
"     background-color: background-color: rgb(211,211,211);\n"
"}\n"
"\n"
"")
        self.verticalLayout_3 = QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.dv_edit = QLineEdit(Dialog)
        self.dv_edit.setObjectName(u"dv_edit")

        self.horizontalLayout_2.addWidget(self.dv_edit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.load_json_button = QPushButton(Dialog)
        self.load_json_button.setObjectName(u"load_json_button")

        self.horizontalLayout_3.addWidget(self.load_json_button)

        self.create_json_button = QPushButton(Dialog)
        self.create_json_button.setObjectName(u"create_json_button")

        self.horizontalLayout_3.addWidget(self.create_json_button)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.json_file_label = QLabel(Dialog)
        self.json_file_label.setObjectName(u"json_file_label")

        self.verticalLayout_2.addWidget(self.json_file_label)

        self.meta_browser = QTextBrowser(Dialog)
        self.meta_browser.setObjectName(u"meta_browser")

        self.verticalLayout_2.addWidget(self.meta_browser)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cancel_button = QPushButton(Dialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.ok_button = QPushButton(Dialog)
        self.ok_button.setObjectName(u"ok_button")

        self.horizontalLayout.addWidget(self.ok_button)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.return_label = QLabel(Dialog)
        self.return_label.setObjectName(u"return_label")

        self.verticalLayout.addWidget(self.return_label)


        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.error_label = QLabel(Dialog)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout_3.addWidget(self.error_label)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Dataverse Collection", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Metadata", None))
        self.load_json_button.setText(QCoreApplication.translate("Dialog", u"Load metadata json", None))
        self.create_json_button.setText(QCoreApplication.translate("Dialog", u"Create minimal metadata", None))
        self.json_file_label.setText("")
        self.cancel_button.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.ok_button.setText(QCoreApplication.translate("Dialog", u"Ok", None))
        self.return_label.setText("")
        self.error_label.setText("")
    # retranslateUi

