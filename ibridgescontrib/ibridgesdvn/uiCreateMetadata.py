"""Widgets for dialog."""
# -*- coding: utf-8 -*-
# pylint: skip-file
# ruff: noqa: N999, E501, N801, D101, N802, D102, N803, N802, D102, N803

################################################################################
## Form generated from reading UI file 'metadata_form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(1067, 519)
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
        self.verticalLayout_7 = QVBoxLayout(Dialog)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QLabel(Dialog)
        self.label.setObjectName("label")

        self.verticalLayout_2.addWidget(self.label)

        self.author_edit = QLineEdit(Dialog)
        self.author_edit.setObjectName("author_edit")

        self.verticalLayout_2.addWidget(self.author_edit)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName("label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.affiliation_edit = QLineEdit(Dialog)
        self.affiliation_edit.setObjectName("affiliation_edit")

        self.verticalLayout_2.addWidget(self.affiliation_edit)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.author_button = QPushButton(Dialog)
        self.author_button.setObjectName("author_button")

        self.horizontalLayout.addWidget(self.author_button)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout_5.addLayout(self.verticalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName("label_3")

        self.verticalLayout_3.addWidget(self.label_3)

        self.contact_name_edit = QLineEdit(Dialog)
        self.contact_name_edit.setObjectName("contact_name_edit")

        self.verticalLayout_3.addWidget(self.contact_name_edit)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName("label_4")

        self.verticalLayout_3.addWidget(self.label_4)

        self.contact_email_edit = QLineEdit(Dialog)
        self.contact_email_edit.setObjectName("contact_email_edit")

        self.verticalLayout_3.addWidget(self.contact_email_edit)

        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.contact_button = QPushButton(Dialog)
        self.contact_button.setObjectName("contact_button")

        self.horizontalLayout_2.addWidget(self.contact_button)

        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_7 = QLabel(Dialog)
        self.label_7.setObjectName("label_7")

        self.verticalLayout_4.addWidget(self.label_7)

        self.title_edit = QLineEdit(Dialog)
        self.title_edit.setObjectName("title_edit")

        self.verticalLayout_4.addWidget(self.title_edit)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName("label_5")

        self.verticalLayout_4.addWidget(self.label_5)

        self.description_edit = QLineEdit(Dialog)
        self.description_edit.setObjectName("description_edit")

        self.verticalLayout_4.addWidget(self.description_edit)

        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName("label_6")

        self.verticalLayout_4.addWidget(self.label_6)

        self.subject_box = QComboBox(Dialog)
        self.subject_box.setObjectName("subject_box")

        self.verticalLayout_4.addWidget(self.subject_box)

        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.subject_button = QPushButton(Dialog)
        self.subject_button.setObjectName("subject_button")

        self.horizontalLayout_3.addWidget(self.subject_button)

        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4.addLayout(self.verticalLayout_5)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.json_edit = QTextEdit(Dialog)
        self.json_edit.setObjectName("json_edit")

        self.verticalLayout_6.addWidget(self.json_edit)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.cancel_button = QPushButton(Dialog)
        self.cancel_button.setObjectName("cancel_button")

        self.horizontalLayout_5.addWidget(self.cancel_button)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.ok_button = QPushButton(Dialog)
        self.ok_button.setObjectName("ok_button")

        self.horizontalLayout_5.addWidget(self.ok_button)

        self.verticalLayout_6.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4.addLayout(self.verticalLayout_6)

        self.verticalLayout_7.addLayout(self.horizontalLayout_4)

        self.error_label = QLabel(Dialog)
        self.error_label.setObjectName("error_label")

        self.verticalLayout_7.addWidget(self.error_label)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", "Author (Last, First)", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", "Affiliation", None))
        self.author_button.setText(QCoreApplication.translate("Dialog", ">>", None))
        self.label_3.setText(
            QCoreApplication.translate("Dialog", "Contact name (Last, First)", None)
        )
        self.label_4.setText(QCoreApplication.translate("Dialog", "Contact e-mail", None))
        self.contact_button.setText(QCoreApplication.translate("Dialog", ">>", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", "Title", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", "Description", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", "Subject", None))
        self.subject_button.setText(QCoreApplication.translate("Dialog", ">>", None))
        self.cancel_button.setText(QCoreApplication.translate("Dialog", "Cancel", None))
        self.ok_button.setText(QCoreApplication.translate("Dialog", "OK", None))
        self.error_label.setText("")

    # retranslateUi
