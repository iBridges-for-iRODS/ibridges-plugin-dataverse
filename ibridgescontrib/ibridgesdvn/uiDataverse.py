"""Widgets for tab."""
# pylint: skip-file
# ruff: noqa: N999, E501, N801, D101, N802, D102, N803, N802, D102, N803

# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tabDataverse.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTreeView,
    QVBoxLayout,
)


class Ui_tabDataverse(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(886, 464)
        Form.setStyleSheet(u"QWidget\n"
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
        self.verticalLayout_4 = QVBoxLayout(Form)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.dv_url_label = QLabel(Form)
        self.dv_url_label.setObjectName(u"dv_url_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.dv_url_label)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.dv_url_select_box = QComboBox(Form)
        self.dv_url_select_box.setObjectName(u"dv_url_select_box")

        self.verticalLayout.addWidget(self.dv_url_select_box)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.add_url_button = QPushButton(Form)
        self.add_url_button.setObjectName(u"add_url_button")

        self.horizontalLayout.addWidget(self.add_url_button)

        self.delete_url_button = QPushButton(Form)
        self.delete_url_button.setObjectName(u"delete_url_button")

        self.horizontalLayout.addWidget(self.delete_url_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.formLayout.setLayout(0, QFormLayout.FieldRole, self.verticalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout.setItem(1, QFormLayout.LabelRole, self.verticalSpacer)

        self.dv_ds_label = QLabel(Form)
        self.dv_ds_label.setObjectName(u"dv_ds_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.dv_ds_label)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.dv_ds_edit = QLineEdit(Form)
        self.dv_ds_edit.setObjectName(u"dv_ds_edit")

        self.verticalLayout_2.addWidget(self.dv_ds_edit)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.dv_create_ds_button = QPushButton(Form)
        self.dv_create_ds_button.setObjectName(u"dv_create_ds_button")

        self.horizontalLayout_2.addWidget(self.dv_create_ds_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.formLayout.setLayout(2, QFormLayout.FieldRole, self.verticalLayout_2)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.selected_data_table = QTableWidget(Form)
        self.selected_data_table.setObjectName(u"selected_data_table")
        self.selected_data_table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.selected_data_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.verticalLayout_3.addWidget(self.selected_data_table)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.delete_selected_button = QPushButton(Form)
        self.delete_selected_button.setObjectName(u"delete_selected_button")

        self.horizontalLayout_3.addWidget(self.delete_selected_button)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.formLayout.setLayout(3, QFormLayout.FieldRole, self.verticalLayout_3)

        self.dv_push_button = QPushButton(Form)
        self.dv_push_button.setObjectName(u"dv_push_button")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.dv_push_button)


        self.horizontalLayout_4.addLayout(self.formLayout)

        self.add_selected_button = QPushButton(Form)
        self.add_selected_button.setObjectName(u"add_selected_button")
        icon = QIcon()
        icon.addFile(u"../../../iBridges-Gui/ibridgesgui/icons/arrow-left.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.add_selected_button.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.add_selected_button)

        self.irods_tree_view = QTreeView(Form)
        self.irods_tree_view.setObjectName(u"irods_tree_view")
        self.irods_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

        self.horizontalLayout_4.addWidget(self.irods_tree_view)


        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.error_label = QLabel(Form)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout_4.addWidget(self.error_label)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.dv_url_label.setText(QCoreApplication.translate("Form", u"Dataverse URL", None))
        self.add_url_button.setText(QCoreApplication.translate("Form", u"Add URL", None))
        self.delete_url_button.setText(QCoreApplication.translate("Form", u"Delete URL", None))
        self.dv_ds_label.setText(QCoreApplication.translate("Form", u"Dataset", None))
        self.dv_create_ds_button.setText(QCoreApplication.translate("Form", u"Create Dataset", None))
        self.label.setText(QCoreApplication.translate("Form", u"Selected data:", None))
        self.delete_selected_button.setText(QCoreApplication.translate("Form", u"Delete", None))
        self.dv_push_button.setText(QCoreApplication.translate("Form", u"Upload to Dataverse", None))
        self.add_selected_button.setText("")
        self.error_label.setText("")
    # retranslateUi

