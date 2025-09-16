"""Widgets for dialog."""
# pylint: skip-file
# ruff: noqa: N999, E501, N801, D101, N802, D102, N803, N802, D102, N803
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_dataset.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(826, 461)
        Dialog.setStyleSheet(
            "QWidget\n"
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
            ""
        )
        self.verticalLayout_3 = QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QLabel(Dialog)
        self.label.setObjectName("label")

        self.horizontalLayout_2.addWidget(self.label)

        self.dv_edit = QLineEdit(Dialog)
        self.dv_edit.setObjectName("dv_edit")

        self.horizontalLayout_2.addWidget(self.dv_edit)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.load_json_button = QPushButton(Dialog)
        self.load_json_button.setObjectName("load_json_button")

        self.horizontalLayout_3.addWidget(self.load_json_button)

        self.create_json_button = QPushButton(Dialog)
        self.create_json_button.setObjectName("create_json_button")

        self.horizontalLayout_3.addWidget(self.create_json_button)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.json_file_label = QLabel(Dialog)
        self.json_file_label.setObjectName("json_file_label")

        self.verticalLayout_2.addWidget(self.json_file_label)

        self.meta_browser = QTextBrowser(Dialog)
        self.meta_browser.setObjectName("meta_browser")

        self.verticalLayout_2.addWidget(self.meta_browser)

        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancel_button = QPushButton(Dialog)
        self.cancel_button.setObjectName("cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.ok_button = QPushButton(Dialog)
        self.ok_button.setObjectName("ok_button")

        self.horizontalLayout.addWidget(self.ok_button)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.return_label = QLabel(Dialog)
        self.return_label.setObjectName("return_label")

        self.verticalLayout.addWidget(self.return_label)

        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.error_label = QLabel(Dialog)
        self.error_label.setObjectName("error_label")

        self.verticalLayout_3.addWidget(self.error_label)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", "Dataverse Collection", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", "Metadata", None))
        self.load_json_button.setText(
            QCoreApplication.translate("Dialog", "Load metadata json", None)
        )
        self.create_json_button.setText(
            QCoreApplication.translate("Dialog", "Create minimal metadata", None)
        )
        self.json_file_label.setText("")
        self.cancel_button.setText(QCoreApplication.translate("Dialog", "Cancel", None))
        self.ok_button.setText(QCoreApplication.translate("Dialog", "Ok", None))
        self.return_label.setText("")
        self.error_label.setText("")

    # retranslateUi
