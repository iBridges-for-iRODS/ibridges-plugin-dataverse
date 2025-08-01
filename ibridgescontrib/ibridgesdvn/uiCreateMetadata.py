# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'metadata_form.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(1067, 519)
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
        self.verticalLayout_7 = QVBoxLayout(Dialog)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.author_edit = QLineEdit(Dialog)
        self.author_edit.setObjectName(u"author_edit")

        self.verticalLayout_2.addWidget(self.author_edit)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.affiliation_edit = QLineEdit(Dialog)
        self.affiliation_edit.setObjectName(u"affiliation_edit")

        self.verticalLayout_2.addWidget(self.affiliation_edit)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.author_button = QPushButton(Dialog)
        self.author_button.setObjectName(u"author_button")

        self.horizontalLayout.addWidget(self.author_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_5.addLayout(self.verticalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_3.addWidget(self.label_3)

        self.contact_name_edit = QLineEdit(Dialog)
        self.contact_name_edit.setObjectName(u"contact_name_edit")

        self.verticalLayout_3.addWidget(self.contact_name_edit)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_3.addWidget(self.label_4)

        self.contact_email_edit = QLineEdit(Dialog)
        self.contact_email_edit.setObjectName(u"contact_email_edit")

        self.verticalLayout_3.addWidget(self.contact_email_edit)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.contact_button = QPushButton(Dialog)
        self.contact_button.setObjectName(u"contact_button")

        self.horizontalLayout_2.addWidget(self.contact_button)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_7 = QLabel(Dialog)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_4.addWidget(self.label_7)

        self.title_edit = QLineEdit(Dialog)
        self.title_edit.setObjectName(u"title_edit")

        self.verticalLayout_4.addWidget(self.title_edit)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_4.addWidget(self.label_5)

        self.description_edit = QLineEdit(Dialog)
        self.description_edit.setObjectName(u"description_edit")

        self.verticalLayout_4.addWidget(self.description_edit)

        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_4.addWidget(self.label_6)

        self.subject_box = QComboBox(Dialog)
        self.subject_box.setObjectName(u"subject_box")

        self.verticalLayout_4.addWidget(self.subject_box)


        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.subject_button = QPushButton(Dialog)
        self.subject_button.setObjectName(u"subject_button")

        self.horizontalLayout_3.addWidget(self.subject_button)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_4.addLayout(self.verticalLayout_5)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.json_edit = QTextEdit(Dialog)
        self.json_edit.setObjectName(u"json_edit")

        self.verticalLayout_6.addWidget(self.json_edit)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.ok_button = QPushButton(Dialog)
        self.ok_button.setObjectName(u"ok_button")

        self.horizontalLayout_5.addWidget(self.ok_button)

        self.cancel_button = QPushButton(Dialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout_5.addWidget(self.cancel_button)


        self.verticalLayout_6.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_4.addLayout(self.verticalLayout_6)


        self.verticalLayout_7.addLayout(self.horizontalLayout_4)

        self.error_label = QLabel(Dialog)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout_7.addWidget(self.error_label)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Author (Last, First)", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Affiliation", None))
        self.author_button.setText(QCoreApplication.translate("Dialog", u">>", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Contact name (Last, First)", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Contact e-mail", None))
        self.contact_button.setText(QCoreApplication.translate("Dialog", u">>", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"Title", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Description", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Subject", None))
        self.subject_button.setText(QCoreApplication.translate("Dialog", u">>", None))
        self.ok_button.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.cancel_button.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.error_label.setText("")
    # retranslateUi

