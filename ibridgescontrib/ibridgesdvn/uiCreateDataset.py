"""Widgets for dialog."""
# -*- coding: utf-8 -*-
# pylint: skip-file
# ruff: noqa: N999, E501, N801, D101, N802, D102, N803, N802, D102, N803

################################################################################
## Form generated from reading UI file 'create_dataset.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
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
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.json_file_label = QLabel(Dialog)
        self.json_file_label.setObjectName("json_file_label")

        self.gridLayout.addWidget(self.json_file_label, 1, 2, 1, 1)

        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName("label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 2)

        self.error_label = QLabel(Dialog)
        self.error_label.setObjectName("error_label")

        self.gridLayout.addWidget(self.error_label, 3, 0, 1, 1)

        self.dv_edit = QLineEdit(Dialog)
        self.dv_edit.setObjectName("dv_edit")

        self.gridLayout.addWidget(self.dv_edit, 0, 2, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName("label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancel_button = QPushButton(Dialog)
        self.cancel_button.setObjectName("cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.ok_button = QPushButton(Dialog)
        self.ok_button.setObjectName("ok_button")

        self.horizontalLayout.addWidget(self.ok_button)

        self.gridLayout.addLayout(self.horizontalLayout, 4, 1, 1, 2)

        self.load_json_button = QPushButton(Dialog)
        self.load_json_button.setObjectName("load_json_button")

        self.gridLayout.addWidget(self.load_json_button, 2, 2, 1, 1)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.json_file_label.setText("")
        self.label_3.setText(QCoreApplication.translate("Dialog", "Metadata file", None))
        self.error_label.setText("")
        self.label.setText(QCoreApplication.translate("Dialog", "Dataverse Collection", None))
        self.cancel_button.setText(QCoreApplication.translate("Dialog", "Cancel", None))
        self.ok_button.setText(QCoreApplication.translate("Dialog", "Ok", None))
        self.load_json_button.setText(QCoreApplication.translate("Dialog", "Load json", None))

    # retranslateUi
