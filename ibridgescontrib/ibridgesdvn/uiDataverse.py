# -*- coding: utf-8 -*-
# pylint: skip-file
# ruff: noqa: N999, E501, N801, D101, N802, D102, N803, N802, D102, N803
################################################################################
## Form generated from reading UI file 'tabDataverse.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QTreeView, QVBoxLayout,
    QWidget)

class Ui_Form(object):
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
"QProgressBar::chunk\n"
"{\n"
"  background-color: rgb(21, 165, 137);\n"
"  width: 5px;\n"
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
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.dv_url_label = QLabel(Form)
        self.dv_url_label.setObjectName(u"dv_url_label")

        self.verticalLayout_3.addWidget(self.dv_url_label)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.dv_url_select_box = QComboBox(Form)
        self.dv_url_select_box.setObjectName(u"dv_url_select_box")
        self.dv_url_select_box.setMinimumSize(QSize(200, 0))

        self.verticalLayout_2.addWidget(self.dv_url_select_box)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.delete_url_button = QPushButton(Form)
        self.delete_url_button.setObjectName(u"delete_url_button")

        self.horizontalLayout_6.addWidget(self.delete_url_button)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)

        self.add_url_button = QPushButton(Form)
        self.add_url_button.setObjectName(u"add_url_button")

        self.horizontalLayout_6.addWidget(self.add_url_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_7.addWidget(self.label_3)

        self.dv_ds_edit = QLineEdit(Form)
        self.dv_ds_edit.setObjectName(u"dv_ds_edit")

        self.horizontalLayout_7.addWidget(self.dv_ds_edit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.dv_create_ds_button = QPushButton(Form)
        self.dv_create_ds_button.setObjectName(u"dv_create_ds_button")

        self.horizontalLayout_2.addWidget(self.dv_create_ds_button)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.check_checksum_box = QCheckBox(Form)
        self.check_checksum_box.setObjectName(u"check_checksum_box")
        self.check_checksum_box.setChecked(True)

        self.verticalLayout_3.addWidget(self.check_checksum_box)

        self.selected_data_table = QTableWidget(Form)
        if (self.selected_data_table.columnCount() < 2):
            self.selected_data_table.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.selected_data_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.selected_data_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.selected_data_table.setObjectName(u"selected_data_table")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selected_data_table.sizePolicy().hasHeightForWidth())
        self.selected_data_table.setSizePolicy(sizePolicy)
        self.selected_data_table.setMinimumSize(QSize(0, 0))
        self.selected_data_table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.selected_data_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.verticalLayout_3.addWidget(self.selected_data_table)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.delete_selected_button = QPushButton(Form)
        self.delete_selected_button.setObjectName(u"delete_selected_button")

        self.horizontalLayout_3.addWidget(self.delete_selected_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.dv_push_button = QPushButton(Form)
        self.dv_push_button.setObjectName(u"dv_push_button")

        self.horizontalLayout_3.addWidget(self.dv_push_button)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.status_label = QLabel(Form)
        self.status_label.setObjectName(u"status_label")

        self.verticalLayout_3.addWidget(self.status_label)

        self.progress_bar = QProgressBar(Form)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(0)

        self.verticalLayout_3.addWidget(self.progress_bar)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.add_selected_button = QPushButton(Form)
        self.add_selected_button.setObjectName(u"add_selected_button")
        font = QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setKerning(True)
        self.add_selected_button.setFont(font)
        self.add_selected_button.setIconSize(QSize(50, 50))

        self.horizontalLayout.addWidget(self.add_selected_button)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.irods_tree_view = QTreeView(Form)
        self.irods_tree_view.setObjectName(u"irods_tree_view")
        self.irods_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.irods_tree_view.setHeaderHidden(True)

        self.verticalLayout_5.addWidget(self.irods_tree_view)

        self.error_label = QLabel(Form)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout_5.addWidget(self.error_label)


        self.horizontalLayout.addLayout(self.verticalLayout_5)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.dv_url_label.setText(QCoreApplication.translate("Form", u"Dataverse URL", None))
#if QT_CONFIG(tooltip)
        self.delete_url_button.setToolTip(QCoreApplication.translate("Form", u"\"Delete a Dataverse configuration.\"", None))
#endif // QT_CONFIG(tooltip)
        self.delete_url_button.setText(QCoreApplication.translate("Form", u"Delete URL", None))
#if QT_CONFIG(tooltip)
        self.add_url_button.setToolTip(QCoreApplication.translate("Form", u"\"Create a new Dataverse configuration.\"", None))
#endif // QT_CONFIG(tooltip)
        self.add_url_button.setText(QCoreApplication.translate("Form", u"Add URL", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Dataset", None))
#if QT_CONFIG(tooltip)
        self.dv_ds_edit.setToolTip(QCoreApplication.translate("Form", u"Fill in a Dataset DOI without \"doi:\".", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.dv_create_ds_button.setToolTip(QCoreApplication.translate("Form", u"\"Create new dataset.\"", None))
#endif // QT_CONFIG(tooltip)
        self.dv_create_ds_button.setText(QCoreApplication.translate("Form", u"Create New Dataset", None))
        self.check_checksum_box.setText(QCoreApplication.translate("Form", u"Compare checksums", None))
        ___qtablewidgetitem = self.selected_data_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Form", u"Path", None));
        ___qtablewidgetitem1 = self.selected_data_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Form", u"Size", None));
#if QT_CONFIG(tooltip)
        self.delete_selected_button.setToolTip(QCoreApplication.translate("Form", u"\"Remove file(s) from table.\"", None))
#endif // QT_CONFIG(tooltip)
        self.delete_selected_button.setText(QCoreApplication.translate("Form", u"Delete", None))
#if QT_CONFIG(tooltip)
        self.dv_push_button.setToolTip(QCoreApplication.translate("Form", u"\"Upload to Dataverse dataset.\"", None))
#endif // QT_CONFIG(tooltip)
        self.dv_push_button.setText(QCoreApplication.translate("Form", u"Upload to Dataverse", None))
        self.status_label.setText("")
#if QT_CONFIG(tooltip)
        self.add_selected_button.setToolTip(QCoreApplication.translate("Form", u"\"Mark file(s) for upload to Dataverse.\"", None))
#endif // QT_CONFIG(tooltip)
        self.add_selected_button.setText(QCoreApplication.translate("Form", u"<<", None))
        self.error_label.setText("")
    # retranslateUi

