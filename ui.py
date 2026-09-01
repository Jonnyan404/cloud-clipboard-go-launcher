# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
    QWidget)
import resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(595, 197)
        font = QFont()
        font.setFamilies([u"Microsoft YaHei UI"])
        font.setPointSize(10)
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.hostComboBox = QComboBox(self.centralwidget)
        self.hostComboBox.setObjectName(u"hostComboBox")
        self.hostComboBox.setMinimumSize(QSize(150, 0))
        self.hostComboBox.setMaxVisibleItems(9)

        self.horizontalLayout.addWidget(self.hostComboBox)

        self.horizontalSpacer_2 = QSpacerItem(48, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.portSpinBox = QSpinBox(self.centralwidget)
        self.portSpinBox.setObjectName(u"portSpinBox")
        self.portSpinBox.setMinimum(1)
        self.portSpinBox.setMaximum(65536)
        self.portSpinBox.setValue(3000)

        self.horizontalLayout.addWidget(self.portSpinBox)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.fileLineEdit = QLineEdit(self.centralwidget)
        self.fileLineEdit.setObjectName(u"fileLineEdit")

        self.horizontalLayout_2.addWidget(self.fileLineEdit)

        self.fileChooseBtn = QPushButton(self.centralwidget)
        self.fileChooseBtn.setObjectName(u"fileChooseBtn")

        self.horizontalLayout_2.addWidget(self.fileChooseBtn)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_3.addWidget(self.label_4)

        self.videoLineEdit = QLineEdit(self.centralwidget)
        self.videoLineEdit.setObjectName(u"videoLineEdit")

        self.horizontalLayout_3.addWidget(self.videoLineEdit)

        self.videoChooseBtn = QPushButton(self.centralwidget)
        self.videoChooseBtn.setObjectName(u"videoChooseBtn")

        self.horizontalLayout_3.addWidget(self.videoChooseBtn)


        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.proxySettingsBtn = QPushButton(self.centralwidget)
        self.proxySettingsBtn.setObjectName(u"proxySettingsBtn")

        self.horizontalLayout_4.addWidget(self.proxySettingsBtn)

        self.horizontalSpacer = QSpacerItem(98, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.aboutBtn = QPushButton(self.centralwidget)
        self.aboutBtn.setObjectName(u"aboutBtn")

        self.horizontalLayout_4.addWidget(self.aboutBtn)

        self.updateBtn = QPushButton(self.centralwidget)
        self.updateBtn.setObjectName(u"updateBtn")

        self.horizontalLayout_4.addWidget(self.updateBtn)

        self.openWebBtn = QPushButton(self.centralwidget)
        self.openWebBtn.setObjectName(u"openWebBtn")

        self.horizontalLayout_4.addWidget(self.openWebBtn)

        self.startBtn = QPushButton(self.centralwidget)
        self.startBtn.setObjectName(u"startBtn")

        self.horizontalLayout_4.addWidget(self.startBtn)


        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.hostComboBox.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"cloud-clipboard-go \u542f\u52a8\u5668", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u670d\u52a1\u76d1\u542c\u5730\u5740\uff1a", None))
        self.hostComboBox.setCurrentText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u670d\u52a1\u76d1\u542c\u7aef\u53e3\uff1a", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u6307\u5b9a\u914d\u7f6e\u6587\u4ef6\uff1a", None))
        self.fileChooseBtn.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u8def\u5f84", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e\u8ba4\u8bc1\u5bc6\u7801\uff1a", None))
        self.videoChooseBtn.setText(QCoreApplication.translate("MainWindow", u"\u67e5\u770b\u5bc6\u7801", None))
        self.proxySettingsBtn.setText(QCoreApplication.translate("MainWindow", u"\u4ee3\u7406\u8bbe\u7f6e", None))
        self.aboutBtn.setText(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e", None))
        self.updateBtn.setText(QCoreApplication.translate("MainWindow", u"\u68c0\u67e5\u66f4\u65b0", None))
        self.openWebBtn.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u7f51\u7ad9", None))
        self.startBtn.setText(QCoreApplication.translate("MainWindow", u"\u542f\u52a8", None))
    # retranslateUi

