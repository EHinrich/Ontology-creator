import sys
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from anytree.importer import JsonImporter
from anytree.exporter import JsonExporter                                                                                                           
from anytree import *
from anytree.exporter import UniqueDotExporter
from PyQt5 import QtCore as qtc
import csv
import matplotlib.pyplot as plt
import json
import networkx as nx
from networkx.readwrite import json_graph
import netgraph
import matplotlib.pyplot as plt; plt.ion()
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.uic import loadUi
import pylab
import os
import types
from treelib import Node as Node_treelib, Tree

from generativepy.color import Color
from generativepy.formulas import rasterise_formula

from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

original_stdout = sys.stdout 

# synchronize state with the new models package
from ontology_app import models, viz, storage

# make sure database exists and default user is ready
storage.init_db()

# expose compatible locals
tree = models.tree
last_id = models.last_id
series = models.series
abstract = models.abstract
"""the variables above are aliases to the models package; the
"global" declarations are unnecessary and caused a syntax error when the
aliases were assigned before the keyword."""


opened = False

class LoginWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent if isinstance(parent, Window) else None
        self.setWindowTitle("Log in")
        self.input_user_name = QLabel(self) #Поля ввода элемента
        self.input_user_name.setText("Login")
        self.input_user_name.setGeometry(125, 10, 100, 100)
        self.e2 = qtw.QLineEdit(self)
        self.e2.setGeometry(75, 70, 150, 25)
        font = self.e2.font()
        font.setPointSize(11)
        self.input_password = QLabel(self)
        self.input_password.setText("Password")
        self.input_password.setGeometry(270, 10, 100, 100)
        self.e3 = qtw.QLineEdit(self)
        self.e3.setGeometry(230, 70, 150, 25)
        self.button_enter8=QPushButton(self)
        self.button_enter8.setText("Log in")
        self.button_enter8.setGeometry(180, 100, 100, 25)
        self.button_enter8.clicked.connect(self.confirm)
        self.space = QLabel(self)
        self.space.setGeometry(175, 140, 100, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def confirm(self):  
        login = self.e2.text()
        password = self.e3.text()
        from ontology_app import storage
        if storage.check_user(login, password):
            self.hide()
            if self.main_window:
                self.main_window.setEnabled(True)
            self.submitClicked.emit(login)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")


class AddClassWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Add class")
            self.input_class=qtw.QLabel(self)
            self.input_class.setText("Class name")
            self.input_class.setGeometry(180, 10, 60, 100)
            self.e1=qtw.QLineEdit(self)
            self.e1.setGeometry(130, 70, 150, 25)
            self.input_type=qtw.QLabel(self)
            self.input_type.setText("Type")
            self.input_type.setGeometry(310, 10, 60, 100)
            self.e11 = QComboBox(self)
            self.e11.setGeometry(290, 70, 70, 25)
            self.e11.addItem("Object")
            self.e11.addItem("Abstract")
            self.button_enter1=qtw.QPushButton(self)
            self.button_enter1.setText("Add")
            self.button_enter1.setGeometry(175, 100, 100, 25)
            self.button_enter1.clicked.connect(self.confirm)
            self.space = QLabel(self)
            self.space.setGeometry(175, 140, 100, 25)
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
    def confirm(self):  
            self.submitClicked.emit(self.e1.text())
            self.close()

class DelClassWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Delete class")
            self.input_class=qtw.QLabel(self)
            self.input_class.setText("Class name")
            self.input_class.setGeometry(120, 10, 60, 100)
            self.e11 = QComboBox(self)
            self.e11.setGeometry(70, 70, 150, 25)
            self.e11.setEditable(True)
            for pre, fill, node in RenderTree(tree):
                if (node.id!="Null"):
                    if (node.name!="•" and "null1" in node.parent.id):
                        self.e11.addItem(node.name)
            self.input_type=qtw.QLabel(self)
            self.button_enter1=qtw.QPushButton(self)
            self.button_enter1.setText("Delete")
            self.button_enter1.setGeometry(95, 100, 100, 25)
            self.button_enter1.clicked.connect(self.confirm)
            self.space = QLabel(self)
            self.space.setGeometry(175, 140, 100, 25)
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
    def confirm(self):  
            self.submitClicked.emit(self.e11.currentText())
            self.close()      

class AddElemWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add element")
        self.input_class_of_elem = QLabel(self) #Поля ввода элемента
        self.input_class_of_elem.setText("Class name")
        self.input_class_of_elem.setGeometry(125, 10, 100, 100)
        self.e2 = QComboBox(self)
        self.e2.setGeometry(75, 70, 150, 25)
        self.e2.setEditable(True)
        font = self.e2.font()
        font.setPointSize(11)
        #self.e2.setFont(font)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.e2.addItem(node.name)
        self.input_elem = QLabel(self)
        self.input_elem.setText("Element name")
        self.input_elem.setGeometry(270, 10, 100, 100)
        self.e3 = qtw.QLineEdit(self)
        self.e3.setGeometry(230, 70, 150, 25)
        #self.e3.setFont(font)
        self.button_enter2=QPushButton(self)
        self.button_enter2.setText("Add")
        self.button_enter2.setGeometry(250, 100, 100, 25)
        self.button_enter2.clicked.connect(self.confirm)
        self.space = QLabel(self)
        self.space.setGeometry(175, 140, 100, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.e2.activated[int].connect(self.class_choosen)

    def class_choosen(self):
        current_class = self.e2.currentText()
        for pre, fill, node in RenderTree(tree):
            if current_class + "abstract" == node.id:
                self.w2_1 = AddElemWindowAbstract(current_class,"", "", "")
                self.w2_1.show()
                self.close()

    def confirm(self): 
        self.submitClicked.emit(self.e3.text())
        self.close()

class AddElemWindowAbstract(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, abstract_class, current_class, current_elem, current_node, parent=None):
        super().__init__(parent)
        self.setGeometry(200,200,1250,700)
        self.abstract_class = abstract_class
        self.current_class = current_class
        self.current_elem = current_elem
        self.current_node = current_node
        self.setWindowTitle("Add element for abstract class " + abstract_class)
        self.main_elem_name = QLabel(self)
        self.main_elem_name.setText("You are currently working with element: "+ current_elem)
        self.main_elem_name.setGeometry(830, 0, 400, 50)
        self.main_elem_name.setFont(QFont('Arial', 12))

        self.input_class_of_elem = QLabel(self) #Поля ввода предметного класса
        self.input_class_of_elem.setText("Object class name")
        self.input_class_of_elem.setGeometry(855, 50, 120, 20)
        self.class_of_main_elem = QComboBox(self)
        self.class_of_main_elem.setGeometry(825, 70, 150, 25)
        self.class_of_main_elem.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_of_main_elem.addItem(node.name)
        self.class_of_main_elem.setCurrentText(current_class)

        self.input_main_elem = QLabel(self)
        self.input_main_elem.setText("Element name")
        self.input_main_elem.setGeometry(1020, 50, 100, 20)
        self.main_elem = QComboBox(self)
        self.main_elem.setGeometry(980, 70, 150, 25)
        self.main_elem.setEditable(True)
        self.main_elem.setCurrentText(current_elem)
        self.class_of_main_elem.activated[int].connect(self.main_class_choosen)

        self.button_load = QPushButton(self)
        self.button_load.setText("Load")
        self.button_load.setGeometry(925, 110, 100, 25)
        self.button_load.clicked.connect(self.load_elem)

        self.input_pair = QLabel(self)
        self.input_pair.setText("Add RDF triple into structure:")
        self.input_pair.setGeometry(880, 160, 400, 50)
        self.input_pair.setFont(QFont('Arial', 12))

        self.input_class_for_elem1 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem1.setText("First class name")
        self.input_class_for_elem1.setGeometry(770, 200, 100, 20)
        self.class_for_elem1_triple = QComboBox(self)
        self.class_for_elem1_triple.setGeometry(745, 220, 150, 25)
        self.class_for_elem1_triple.setEditable(True)
        self.input_class_for_elem2 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem2.setText("Second class name")
        self.input_class_for_elem2.setGeometry(1085, 200, 100, 20)
        self.class_for_elem2_triple = QComboBox(self)
        self.class_for_elem2_triple.setGeometry(1055, 220, 150, 25)
        self.class_for_elem2_triple.setEditable(True)

        self.input_elem1 = QLabel(self) #Поля ввода элемента
        self.input_elem1.setText("First element name")
        self.input_elem1.setGeometry(775, 260, 120, 20)
        self.elem1_tiple = QComboBox(self)
        self.elem1_tiple.setGeometry(745, 280, 150, 25)
        self.elem1_tiple.setEditable(True)
        self.input_rel_triple = QLabel(self) #Поля ввода отношения
        self.input_rel_triple.setText("Relationship name")
        self.input_rel_triple.setGeometry(940, 260, 100, 20)
        self.rel_triple = QLineEdit(self)
        self.rel_triple.setGeometry(900, 280, 150, 25)
        self.input_elem2 = QLabel(self) #Поля ввода элемента
        self.input_elem2.setText("Second element name")
        self.input_elem2.setGeometry(1075, 260, 120, 20)
        self.elem2_triple = QComboBox(self)
        self.elem2_triple.setGeometry(1055, 280, 150, 25)
        self.elem2_triple.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_for_elem1_triple.addItem(node.name)
                    self.class_for_elem2_triple.addItem(node.name)
        self.button_add_triple=QPushButton(self)
        self.button_add_triple.setText("Add triple")
        self.button_add_triple.setGeometry(925, 320, 100, 25)
        self.button_add_triple.clicked.connect(self.add_triple)
        self.space = QLabel(self)
        self.space.setGeometry(825, 360, 100, 25)
        self.class_for_elem1_triple.activated[int].connect(self.class1_choosen_triple)
        self.class_for_elem2_triple.activated[int].connect(self.class2_choosen_triple)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.input_one_elem = QLabel(self)
        self.input_one_elem.setText("Add one element into structure:")
        self.input_one_elem.setGeometry(880, 380, 400, 50)
        self.input_one_elem.setFont(QFont('Arial', 12))

        self.input_class_for_elem = QLabel(self) 
        self.input_class_for_elem.setText("Class name")
        self.input_class_for_elem.setGeometry(855, 430, 120, 20)
        self.class_for_elem_one = QComboBox(self)
        self.class_for_elem_one.setGeometry(825, 450, 150, 25)
        self.class_for_elem_one.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_for_elem_one.addItem(node.name)

        self.input_elem = QLabel(self)
        self.input_elem.setText("Element name")
        self.input_elem.setGeometry(1020, 430, 100, 20)
        self.elem_one = QComboBox(self)
        self.elem_one.setGeometry(980, 450, 150, 25)
        self.elem_one.setEditable(True)
        self.class_for_elem_one.activated[int].connect(self.class_choosen_one)

        self.button_add_elem = QPushButton(self)
        self.button_add_elem.setText("Add element")
        self.button_add_elem.setGeometry(925, 490, 100, 25)
        self.button_add_elem.clicked.connect(self.add_elem)

        self.sc = CanvasAbstract(self, current_node)
        self.hlayout = QHBoxLayout()
        self.vlayout1 = QVBoxLayout()
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.hlayout.addLayout(self.vlayout1)
        self.widget = QWidget(self)
        self.widget.setGeometry(0, 0, 700, 700)
        self.widget.setLayout(self.hlayout)

    def refresh_canvas(self):
        self.vlayout1.removeWidget(self.toolbar)
        self.vlayout1.removeWidget(self.sc)
        self.toolbar.setParent(None)
        self.sc.setParent(None)
        self.toolbar.deleteLater()
        self.sc.deleteLater()
        self.sc = CanvasAbstract(self, self.current_node)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.widget.update()

    def main_class_choosen(self):
        current_class = self.class_of_main_elem.currentText()
        current_elem = self.main_elem.currentText()
        self.main_elem.clear()
        node_class = Node(name = "", id ="")
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + "null3" ):
                node_class = node
        if (node_class.id!=""):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.main_elem.addItem(node.name)
        self.main_elem.setCurrentText(current_elem)
    
    def class1_choosen_triple(self): #Вывод списка эл первого класса
        self.elem1_tiple.clear()
        current_class = self.class_for_elem1_triple.currentText()
        node_class = Node(name = "", id ="")
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + "null3"):
                node_class = node
        if (node_class.id!=""):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem1_tiple.addItem(node.name)
        
    def class2_choosen_triple(self): #Вывод списка элементов второго класса
        self.elem2_triple.clear()
        current_class = self.class_for_elem2_triple.currentText()
        node_class = Node(name = "", id ="")
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + "null3"):
                node_class = node
        if (node_class.id!=""):
            for pre, fill, node in RenderTree(tree):
                if (node.id != "Null"):
                    if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                        self.elem2_triple.addItem(node.name)
    
    def class_choosen_one(self):
        self.elem_one.clear()
        current_class = self.class_for_elem_one.currentText()
        node_class = Node(name = "", id ="")
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + "null3"):
                node_class = node
        if (node_class.id!=""):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem_one.addItem(node.name)

    def load_elem(self):
        models.abstract = models.create_abstract_class(models.abstract, "load", self.main_elem.currentText(), self.elem1_tiple.currentText(), self.elem2_triple.currentText(), self.rel_triple.text(), self.elem_one.currentText())
        cur = ""
        for pre, fill, node in RenderTree(models.abstract):
                if self.main_elem.currentText() + "null6" in node.id:
                    cur = node.id
        self.current_node = cur
        self.current_class = self.class_of_main_elem.currentText()
        self.current_elem = self.main_elem.currentText()
        self.main_elem_name.setText("You are currently working with element: " + self.current_elem)
        self.refresh_canvas()

    def add_triple(self):
        models.abstract = models.create_abstract_class(models.abstract, "add RDF triple", self.main_elem.currentText(), self.elem1_tiple.currentText(), self.elem2_triple.currentText(), self.rel_triple.text(), self.elem_one.currentText())
        cur = ""
        for pre, fill, node in RenderTree(models.abstract):
                if self.main_elem.currentText() + "null6" in node.id:
                    cur = node.id
        self.current_node = cur
        self.current_class = self.class_of_main_elem.currentText()
        self.current_elem = self.main_elem.currentText()
        self.main_elem_name.setText("You are currently working with element: " + self.current_elem)
        self.refresh_canvas()

    def add_elem(self):
        models.abstract = models.create_abstract_class(models.abstract, "add element", self.main_elem.currentText(), self.elem1_tiple.currentText(), self.elem2_triple.currentText(), self.rel_triple.text(), self.elem_one.currentText())
        cur = ""
        for pre, fill, node in RenderTree(models.abstract):
                if self.main_elem.currentText() + "null6" in node.id:
                    cur = node.id
        self.current_node = cur
        self.current_class = self.class_of_main_elem.currentText()
        self.current_elem = self.main_elem.currentText()
        self.main_elem_name.setText("You are currently working with element: " + self.current_elem)
        self.refresh_canvas()


class CanvasAbstract(FigureCanvasQTAgg):
    def __init__(self, parent, current_node=None):
        fig, self.ax = plt.subplots(figsize=(7, 7))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        super(CanvasAbstract, self).__init__(fig)
        self.setParent(parent)
        abstract = models.abstract
        k=0
        for pre, fill, node in RenderTree(abstract):
            k+=1
        if k>1:
            viz.draw_abstract_class(abstract, current_node)
            plt.tight_layout()
        plt.close()

class DelElemWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete element")
        self.input_class_of_elem = QLabel(self) #Поля ввода элемента
        self.input_class_of_elem.setText("Class name")
        self.input_class_of_elem.setGeometry(125, 10, 100, 100)
        self.e2 = QComboBox(self)
        self.e2.setGeometry(75, 70, 150, 25)
        self.e2.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.e2.addItem(node.name)

        self.input_elem = QLabel(self)
        self.input_elem.setText("Element name")
        self.input_elem.setGeometry(270, 10, 100, 100)
        self.e7 = QComboBox(self)
        self.e7.setEditable(True)
        self.e7.setGeometry(230, 70, 150, 25)
        self.button_enter2=QPushButton(self)
        self.button_enter2.setText("Delete")
        self.button_enter2.setGeometry(175, 100, 100, 25)
        self.button_enter2.clicked.connect(self.confirm)
        self.space = QLabel(self)
        self.space.setGeometry(175, 140, 100, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.e2.activated[int].connect(self.class_choosen)

    def class_choosen(self): #Вывод списка эл первого класса
        self.e7.clear()
        current_class = self.e2.currentText()
        node_class = Node(name = "", id ="")
        tmp_tree = Node(name=current_class, id = "1")
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + "null3" ):
                node_class = node
        if (node_class.id!=""):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.e7.addItem(node.name)
                    add_elem_list1(tmp_tree, node.name)
            for pre, fill, node in RenderTree(tmp_tree):
                print("%s%s" % (pre, node.name))
        else:
            node1 = Node(name = "•", id = "1")
            Node(name = "•", id = "2", parent=node1)
            Node(name = current_class, id = "3", parent=node1)
        
    def confirm(self): 
        self.submitClicked.emit(self.e7.currentText())
        self.close()

class AddRelClassesWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add relationships between classes")
        self.input_class1 = QLabel(self) #Поля ввода класса
        self.input_class1.setText("First class name")
        self.input_class1.setGeometry(120, 10, 100, 100)
        self.e4 = QComboBox(self)
        self.e4.setGeometry(95, 70, 150, 25)
        self.e4.setEditable(True)
        self.rel1 = QLabel(self) #Поля ввода класса
        self.rel1.setText("Relationship name")
        self.rel1.setGeometry(290, 10, 100, 100)
        self.e5 = QLineEdit(self)
        self.e5.setGeometry(250, 70, 150, 25)
        self.input_class2 = QLabel(self) #Поля ввода класса
        self.input_class2.setText("Second class name")
        self.input_class2.setGeometry(435, 10, 100, 100)
        self.e6 = QComboBox(self)
        self.e6.setGeometry(405, 70, 150, 25)
        self.e6.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.e4.addItem(node.name)
                    self.e6.addItem(node.name)
        self.button_enter3=QPushButton(self)
        self.button_enter3.setText("Add")
        self.button_enter3.setGeometry(275, 110, 100, 25)
        self.button_enter3.clicked.connect(self.confirm)
        self.space = QLabel(self)
        self.space.setGeometry(175, 140, 100, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
    def confirm(self): 
        self.submitClicked.emit(self.e5.text())
        self.close()

class AddRelElemWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(200,200,1250,700)
        self.setWindowTitle("Add relationships between elements")
        self.input_class_for_elem1 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem1.setText("First class name")
        self.input_class_for_elem1.setGeometry(770, -10, 100, 100)
        self.e71 = QComboBox(self)
        self.e71.setGeometry(745, 50, 150, 25)
        self.e71.setEditable(True)
        self.input_class_for_elem2 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem2.setText("Second class name")
        self.input_class_for_elem2.setGeometry(1085, -10, 100, 100)
        self.e91= QComboBox(self)
        self.e91.setGeometry(1055, 50, 150, 25)
        self.e91.setEditable(True)

        self.input_elem1 = QLabel(self) #Поля ввода элемента
        self.input_elem1.setText("First element name")
        self.input_elem1.setGeometry(775, 70, 120, 100)
        self.e7 = QComboBox(self)
        self.e7.setGeometry(745, 130, 150, 25)
        self.e7.setEditable(True)
        self.rel2 = QLabel(self) #Поля ввода отношения
        self.rel2.setText("Relationship name")
        self.rel2.setGeometry(940, 70, 100, 100)
        self.e8 = QLineEdit(self)
        self.e8.setGeometry(900, 130, 150, 25)
        self.input_elem2 = QLabel(self) #Поля ввода элемента
        self.input_elem2.setText("Second element name")
        self.input_elem2.setGeometry(1075, 70, 120, 100)
        self.e9 = QComboBox(self)
        self.e9.setGeometry(1055, 130, 150, 25)
        self.e9.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.e71.addItem(node.name)
                    self.e91.addItem(node.name)
        self.button_enter4=QPushButton(self)
        self.button_enter4.setText("Add")
        self.button_enter4.setGeometry(925, 160, 100, 25)
        self.button_enter4.clicked.connect(self.add)
        self.space = QLabel(self)
        self.space.setGeometry(825, 190, 100, 25)
        self.e71.activated[int].connect(self.class1_choosen)
        self.e91.activated[int].connect(self.class2_choosen)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        self.sc = CanvasElemChoosen(self)
        self.hlayout = QHBoxLayout()
        self.vlayout1 = QVBoxLayout()
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.hlayout.addLayout(self.vlayout1)
        self.widget = QWidget(self)
        self.widget.setGeometry(0, 0, 700, 700)
        self.widget.setLayout(self.hlayout)

    def refresh_canvas(self):
        self.vlayout1.removeWidget(self.toolbar)
        self.vlayout1.removeWidget(self.sc)
        self.toolbar.setParent(None)
        self.sc.setParent(None)
        self.toolbar.deleteLater()
        self.sc.deleteLater()
        self.sc = CanvasElemChoosen(self)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.update()
    
    def class1_choosen(self): #Вывод списка эл первого класса
        self.e7.clear()
        current_class = self.e71.currentText()
        node_class = Node(name = "", id ="")
        tmp_tree = Node(name=current_class, id = "1")
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + "null3"):
                node_class = node
        if (node_class.id!=""):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.e7.addItem(node.name)
                    add_elem_list1(tmp_tree, node.name)
            for pre, fill, node in RenderTree(tmp_tree):
                print("%s%s" % (pre, node.name))
        else:
            node1 = Node(name = "•", id = "1")
            Node(name = "•", id = "2", parent=node1)
            Node(name = current_class, id = "3", parent=node1)
        

    def class2_choosen(self): #Вывод списка элементов второго класса
        self.e9.clear()
        current_class = self.e91.currentText()
        node_class = Node(name = "", id ="")
        tmp_tree = Node(name=current_class, id = "2")
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + "null3"):
                node_class = node
        if (node_class.id!=""):
            for pre, fill, node in RenderTree(tree):
                if (node.id != "Null"):
                    if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                        self.e9.addItem(node.name)
                        add_elem_list2(tmp_tree, node.name)
        else:
            node1 = Node(name = "•", id = "1")
            Node(name = "•", id = "2", parent=node1)
            Node(name = current_class, id = "3", parent=node1)

            
    def add(self):
        add_elements_rel(tree, self.e7.currentText(), self.e8.text(), self.e9.currentText())
        self.refresh_canvas()

class CreateSeriesWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(200,200,1250,700)
        self.setWindowTitle("Create series of elements")
        self.input_class = QLabel(self) #Поле ввода класса
        self.input_class.setText("Class name")
        self.input_class.setGeometry(775, 70, 120, 100)
        self.e71 = QComboBox(self)
        self.e71.setGeometry(745, 130, 150, 25)
        self.e71.setEditable(True)

        self.input_elem = QLabel(self) #Поле ввода элемента
        self.input_elem.setText("Element name")
        self.input_elem.setGeometry(940, 70, 100, 100)
        self.e7 = QComboBox(self)
        self.e7.setGeometry(900, 130, 150, 25)
        self.e7.setEditable(True)
        self.rel = QLabel(self) #Поле ввода отношения
        self.rel.setText("Relationship name")
        self.rel.setGeometry(1075, 70, 120, 100)
        self.e8 = QComboBox(self)
        self.e8.setGeometry(1055, 130, 150, 25)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.e71.addItem(node.name)
        for pre, fill, node in RenderTree(tree):
                if (node.id != "Null"):
                    if (node.name!="•" and node.name + " in elements" == node.id and node.parent.id == node.name + " in elements_rel"):
                        self.e8.addItem(node.name)
        self.button_enter5=QPushButton(self)
        self.button_enter5.setText("Create")
        self.button_enter5.setGeometry(925, 160, 100, 25)
        self.button_enter5.clicked.connect(self.create)
        self.space = QLabel(self)
        self.space.setGeometry(825, 190, 100, 25)
        self.e71.activated[int].connect(self.class_choosen)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        self.sc = CanvasAbstract(self)
        self.hlayout = QHBoxLayout()
        self.vlayout1 = QVBoxLayout()
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.hlayout.addLayout(self.vlayout1)
        self.widget = QWidget(self)
        self.widget.setGeometry(0, 0, 700, 700)
        self.widget.setLayout(self.hlayout)

    def refresh_canvas(self):
        self.vlayout1.removeWidget(self.toolbar)
        self.vlayout1.removeWidget(self.sc)
        self.toolbar.setParent(None)
        self.sc.setParent(None)
        self.toolbar.deleteLater()
        self.sc.deleteLater()
        self.sc = CanvasSeries(self)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.update()

    def class_choosen(self): #Вывод списка элементов класса
        self.e7.clear()
        current_class = self.e71.currentText()
        node_class = Node(name = "", id ="")
        tmp_tree = Node(name=current_class, id = "1")
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + "null3"):
                node_class = node
        if (node_class.id!=""):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.e7.addItem(node.name)
                    #add_elem_list1(tmp_tree, node.name)
            for pre, fill, node in RenderTree(tmp_tree):
                print("%s%s" % (pre, node.name))
        else:
            node1 = Node(name = "•", id = "1")
            Node(name = "•", id = "2", parent=node1)
            Node(name = current_class, id = "3", parent=node1)      
            
    def create(self): 
        models.series = create_series(tree, self.e7.currentText(), self.e8.currentText())
        self.refresh_canvas()

class CanvasSeries(FigureCanvasQTAgg):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(7, 7))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        super(CanvasSeries, self).__init__(fig)
        self.setParent(parent)
        series = models.series
        k=0
        for pre, fill, node in RenderTree(series):
            k+=1
        if k>1:
            draw_series(series)
            fig.tight_layout()
        plt.close()

class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(5, 5))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        super(Canvas, self).__init__(fig)
        self.setParent(parent)
        k=0
        for pre, fill, node in RenderTree(tree):
            k+=1
        if k>1:
            draw_tree(tree)
            fig.tight_layout()
        plt.close()

class CanvasElem(FigureCanvasQTAgg):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(7, 7))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        super(CanvasElem, self).__init__(fig)
        self.setParent(parent)
        plt.close()

class CanvasElemChoosen(FigureCanvasQTAgg):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(7, 7))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        super(CanvasElemChoosen, self).__init__(fig)
        self.setParent(parent)
        draw_class(tree)
        plt.close()


class Window(QMainWindow, QDialog):
    resized = QtCore.pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Ontology ")
        self.setGeometry(100, 100, 600, 400)
        self.initUI()

    def initUI(self):
        QWidget.__init__(self)
        tree = {}
        self.tree = QTreeView(self)
        root_model = QStandardItemModel()
        self.tree.setModel(root_model)
        self._populateTree(tree, root_model.invisibleRootItem())
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        width = self.frameGeometry().width()
        self.resized.connect(self.resize)

        self.warning = QLabel(self)
        self.warning.setText("")
        self.warning.setGeometry(100, 600, 600, 100)

        hlayout = QHBoxLayout()
        vlayout1 = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(hlayout)
        sc = Canvas(self)
        toolbar = NavigationToolbar(sc, self)
        vlayout1.addWidget(toolbar)
        vlayout1.addWidget(sc)
        hlayout.addLayout(vlayout1,stretch=4)
        hlayout.addWidget(self.tree,stretch=1)
        self.setCentralWidget(widget)

        self._createMenuBar()
        toolbar = QToolBar()
        toolbar.setFixedHeight(36)
        self.addToolBar(toolbar)
        toolbar.setStyleSheet("QToolButton{padding: 20px;}")

        button_add_class = QAction("Add class", self)
        button_add_class.setFont(QFont('Times', 10))
        button_add_class.triggered.connect(self.window_add_class)
        toolbar.addAction(button_add_class)

        button_add_elem = QAction("Add element", self)
        button_add_elem.setFont(QFont('Times', 10))
        button_add_elem.triggered.connect(self.window_add_elem)
        toolbar.addAction(button_add_elem)

        button_add_rel_classes = QAction("Add relationships between classes", self)
        button_add_rel_classes.setFont(QFont('Times', 10))
        button_add_rel_classes.triggered.connect(self.window_add_rel_classes)
        toolbar.addAction(button_add_rel_classes)

        button_add_rel_elem = QAction("Add relationships between elements", self)
        button_add_rel_elem.setFont(QFont('Times', 10))
        button_add_rel_elem.triggered.connect(self.window_add_rel_elem)
        toolbar.addAction(button_add_rel_elem)

        button_del_class = QAction("Delete class", self)
        button_del_class.setFont(QFont('Times', 10))
        button_del_class.triggered.connect(self.window_del_class)
        toolbar.addAction(button_del_class)

        button_del_elem = QAction("Delete element", self)
        button_del_elem.setFont(QFont('Times', 10))
        button_del_elem.triggered.connect(self.window_del_elem)
        toolbar.addAction(button_del_elem)

        button_create_series = QAction("Create series", self)
        button_create_series.setFont(QFont('Times', 10))
        button_create_series.triggered.connect(self.window_create_series)
        toolbar.addAction(button_create_series)


    def class_list_tree(self, tree):
        data = {}
        for pre, fill, node in RenderTree(tree):
            if (node.parent!=None):
                if ("null1" in node.parent.id):
                    if (node.name!="•"):
                        current_class=node.name
                        el_data=[]
                        node_class = Node(name = "", id ="")
                        for pre, fill, node in RenderTree(tree):
                            if (node.id == current_class + "null3"):
                                node_class = node
                        if (node_class.id!=""):
                            for pre, fill, node in RenderTree(tree):
                                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                                    el_data.append(node.name)
                        else:
                            el_data.append("")
                        data.update({current_class:el_data})

        json_data = json.dumps(data)
        json_object = json.loads(json_data)
        return json_object

    def _populateTree(self, children, parent):
        for child in sorted(children):
            child_item = QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict):
                self._populateTree(children[child], child_item)

    def _createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&Ontology", self)
        menuBar.addMenu(fileMenu)
        newAction = QAction("&New", self)
        openAction = QAction("&Open...", self)
        saveAction = QAction("&Save", self)
        exitAction = QAction("Exit", self)
        loginAction = QAction("Login", self)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)
        fileMenu.addAction(newAction)
        fileMenu.addAction(loginAction)
        fileMenu.triggered[QAction].connect(self.do_something_ontology)

    def window_login(self):
        self.w8 = LoginWindow()
        self.w8.submitClicked.connect(self.clicked_enter8)
        self.w8.show()


    def window_add_class(self, checked):
        if opened:
            self.w1 = AddClassWindow()
            self.w1.e1.setText("")
            self.w1.submitClicked.connect(self.clicked_enter1)
            self.w1.show()

    def window_del_class(self, checked):
        if opened:
            self.w1_1 = DelClassWindow()
            self.w1_1.submitClicked.connect(self.clicked_enter1_1)
            self.w1_1.show()

    def window_add_elem(self, checked):
        if opened:
            self.w2 = AddElemWindow()
            self.w2.e3.setText("")
            self.w2.submitClicked.connect(self.clicked_enter3)
            self.w2.show()

    def window_del_elem(self, checked):
        if opened:
            self.w3_3 = DelElemWindow()
            self.w3_3.submitClicked.connect(self.clicked_enter3_3)
            self.w3_3.show()

    def window_add_rel_classes(self, checked):
        if opened:
            self.w3 = AddRelClassesWindow()
            self.w3.e5.setText("")
            self.w3.submitClicked.connect(self.clicked_enter2)
            self.w3.show()
    
    def window_add_rel_elem(self, checked):
        if opened:
            self.w4 = AddRelElemWindow()
            self.w4.e8.setText("")
            #self.w4.submitClicked.connect(self.clicked_enter4)
            self.w4.show()

    def window_create_series(self, checked):
        if opened:
            self.w5 = CreateSeriesWindow()
            self.w5.show()

    @pyqtSlot()
    def clicked_enter1(self):  #Перерисовка дерева при добавлении нового класса в онтологию
        self.warning.setText("")
        current1 = self.w1.e1.text()
        if(self.w1.e11.currentText()== "Object"):
            current2="object"
        if(self.w1.e11.currentText()== "Abstract"):
            current2="abstract"
        self.w1.e1.setText("")
        add_class(tree, current1, current2)
        list_tree=self.class_list_tree(tree)
        self.list_tree = QTreeView(self)
        root_model = QStandardItemModel()
        self.list_tree.setModel(root_model)
        self._populateTree(list_tree, root_model.invisibleRootItem())

        hlayout = QHBoxLayout()
        vlayout1 = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(hlayout)
        sc = Canvas(self)
        toolbar = NavigationToolbar(sc, self)
        vlayout1.addWidget(toolbar)
        vlayout1.addWidget(sc)
        hlayout.addLayout(vlayout1,stretch=4)
        hlayout.addWidget(self.list_tree,stretch=1)
        self.setCentralWidget(widget)

        fnt = QFont()
        fnt.setPixelSize(15)
        self.list_tree.setFont(fnt)

    def clicked_enter1_1(self):  #Перерисовка дерева при удалении класса
        self.warning.setText("")
        current1 = self.w1_1.e11.currentText()
        del_class(tree, current1)
        list_tree=self.class_list_tree(tree)
        self.list_tree = QTreeView(self)
        root_model = QStandardItemModel()
        self.list_tree.setModel(root_model)
        self._populateTree(list_tree, root_model.invisibleRootItem())

        hlayout = QHBoxLayout()
        vlayout1 = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(hlayout)
        sc = Canvas(self)
        toolbar = NavigationToolbar(sc, self)
        vlayout1.addWidget(toolbar)
        vlayout1.addWidget(sc)
        hlayout.addLayout(vlayout1,stretch=4)
        hlayout.addWidget(self.list_tree,stretch=1)
        self.setCentralWidget(widget)

        fnt = QFont()
        fnt.setPixelSize(15)
        self.list_tree.setFont(fnt)

    def clicked_enter3(self):  #Перерисовка дерева при добавлении нового элемента в класс онтологии
        self.warning.setText("")
        current1 = self.w2.e2.currentText()
        current2 = self.w2.e3.text()
        self.w2.e3.setText("")
        n=0
        for pre, fill, node in RenderTree(tree):
            if (current1 == node.name and "null1" in node.parent.id):
                n=n+1
        if n==0:
            self.warning.setText("Class " + current1 + ", to which you want to add an element is not present in the ontology")
        else:
            n=0
            for pre, fill, node in RenderTree(tree):
                if (node.id==current1+"formula"):
                    n=n+1
            if (n==0):
                add_elem(tree, current1, current2)
            else:
                add_elem(tree, current1, current2)

        list_tree=self.class_list_tree(tree)
        self.list_tree = QTreeView(self)
        root_model = QStandardItemModel()
        self.list_tree.setModel(root_model)
        self._populateTree(list_tree, root_model.invisibleRootItem())

        hlayout = QHBoxLayout()
        vlayout1 = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(hlayout)
        sc = Canvas(self)
        toolbar = NavigationToolbar(sc, self)
        vlayout1.addWidget(toolbar)
        vlayout1.addWidget(sc)
        hlayout.addLayout(vlayout1,stretch=4)
        hlayout.addWidget(self.list_tree,stretch=1)
        self.setCentralWidget(widget)

        fnt = QFont()
        fnt.setPixelSize(15)
        self.list_tree.setFont(fnt)

    def clicked_enter3_3(self):  #Перерисовка дерева при удалении элемента
        self.warning.setText("")
        current = self.w3_3.e7.currentText()
        del_elem(tree, current)
        exporter = JsonExporter(indent=2, sort_keys=True)
        list_tree=self.class_list_tree(tree)
        self.list_tree = QTreeView(self)
        root_model = QStandardItemModel()
        self.list_tree.setModel(root_model)
        self._populateTree(list_tree, root_model.invisibleRootItem())

        hlayout = QHBoxLayout()
        vlayout1 = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(hlayout)
        sc = Canvas(self)
        toolbar = NavigationToolbar(sc, self)
        vlayout1.addWidget(toolbar)
        vlayout1.addWidget(sc)
        hlayout.addLayout(vlayout1,stretch=4)
        hlayout.addWidget(self.list_tree,stretch=1)
        self.setCentralWidget(widget)

        fnt = QFont()
        fnt.setPixelSize(15)
        self.list_tree.setFont(fnt)
    
    def clicked_enter2(self):  #Перерисовка дерева при добавлении нового отношения между классами
        self.warning.setText("")
        current1 = self.w3.e4.currentText()
        current2 = self.w3.e5.text()
        current3 = self.w3.e6.currentText()
        self.w3.e5.setText("")
        n1=0
        n2=0
        for pre, fill, node in RenderTree(tree):
            if (current1 == node.name and "null1" in node.parent.id):
                n1=n1+1
            if (current3 == node.name and "null1" in node.parent.id):
                n2=n2+1
        if (n1==0 and n2!=0):
            self.warning.setText("Class " + current1 + " is not present in the ontology")
        if (n2==0 and n1!=0):
            self.warning.setText("Class " + current3 + " is not present in the ontology")
        if (n2==0 and n1==0):
            self.warning.setText("Classes " + current1 + " и " + current3 + " are not present in the ontology")
        if (n1!=0 and n2!=0):
            add_classes_rel(tree, current1, current2, current3)

        list_tree=self.class_list_tree(tree)
        self.list_tree = QTreeView(self)
        root_model = QStandardItemModel()
        self.list_tree.setModel(root_model)
        self._populateTree(list_tree, root_model.invisibleRootItem())

        hlayout = QHBoxLayout()
        vlayout1 = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(hlayout)
        sc = Canvas(self)
        toolbar = NavigationToolbar(sc, self)
        vlayout1.addWidget(toolbar)
        vlayout1.addWidget(sc)
        hlayout.addLayout(vlayout1,stretch=4)
        hlayout.addWidget(self.list_tree,stretch=1)
        self.setCentralWidget(widget)

        fnt = QFont()
        fnt.setPixelSize(15)
        self.list_tree.setFont(fnt)

    def clicked_enter4(self):  #Перерисовка дерева при добавлении нового отношения между элементами
        self.warning.setText("")
        current1 = self.w4.e7.currentText()
        current2 = self.w4.e8.text()
        current3 = self.w4.e9.currentText()
        self.w4.e8.setText("")
        n1=0
        n2=0
        for pre, fill, node1 in RenderTree(tree):
            if (node1.id != "Null"):
                if "null1" in node1.parent.id:
                    for pre, fill, node2 in RenderTree(tree):
                        if current1+node1.name == node2.id:
                            n1=n1+1
                        if current3+node1.name == node2.id:
                            n2=n2+1
        if (n1==0 and n2!=0):
            self.warning.setText("Element " + current1 + " is not present in the ontology")
        if (n2==0 and n1!=0):
            self.warning.setText("Element " + current3 + " is not present in the ontology")
        if (n2==0 and n1==0):
            self.warning.setText("Elements " + current1 + " и " + current3 + " are not present in the ontology")
        if (n1!=0 and n2!=0):
            add_elements_rel(tree, current1, current2, current3)

        list_tree=self.class_list_tree(tree)
        self.list_tree = QTreeView(self)
        root_model = QStandardItemModel()
        self.list_tree.setModel(root_model)
        self._populateTree(list_tree, root_model.invisibleRootItem())

        hlayout = QHBoxLayout()
        vlayout1 = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(hlayout)
        sc = Canvas(self)
        toolbar = NavigationToolbar(sc, self)
        vlayout1.addWidget(toolbar)
        vlayout1.addWidget(sc)
        hlayout.addLayout(vlayout1,stretch=4)
        hlayout.addWidget(self.list_tree,stretch=1)
        self.setCentralWidget(widget)

        self.w4 = AddRelElemWindow()
        self.w4.e8.setText("")
        self.w4.submitClicked.connect(self.clicked_enter4)
        self.w4.show()

        fnt = QFont()
        fnt.setPixelSize(15)
        self.list_tree.setFont(fnt)
        

    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(QtWidgets.QAction)
    def do_something_ontology(self, action):
        global tree
        if (action.text()=="&Open..."):
            filename, filetype = QFileDialog.getOpenFileName(
                self, 
                "Open file",
                ".", 
                "Text Files(*.txt)"
            )
            importer = JsonImporter()
            if filename != "":
                load = open(filename)
                j=load.read()
                load.close()
                models.tree = importer.import_(j)
                tree = models.tree
            list_tree=self.class_list_tree(tree)
            self.list_tree = QTreeView(self)
            fnt = QFont()
            fnt.setPixelSize(15)
            self.list_tree.setFont(fnt)
            root_model = QStandardItemModel()
            self.list_tree.setModel(root_model)
            self._populateTree(list_tree, root_model.invisibleRootItem())

            hlayout = QHBoxLayout()
            vlayout1 = QVBoxLayout()
            widget = QWidget()
            widget.setLayout(hlayout)
            sc = Canvas(self)
            toolbar = NavigationToolbar(sc, self)
            vlayout1.addWidget(toolbar)
            vlayout1.addWidget(sc)
            hlayout.addLayout(vlayout1,stretch=4)
            hlayout.addWidget(self.list_tree,stretch=1)
            self.setCentralWidget(widget)
            global opened
            opened = True

        if (action.text()=="&New"):
            format = 'txt'
            initialPath = QDir.currentPath() + "/untitled." + format    
            fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
                    "%s Files (*.%s);;All Files (*)" % (format.upper(), format))
            if fileName:
                base=os.path.basename(fileName)
                os.path.splitext(base)
                file = open(fileName, 'w')
                exporter = JsonExporter(indent=2, sort_keys=True)
                text = exporter.export(tree)
                file.write(text)
                file.close()
                models.tree = create_ontology_tree(os.path.splitext(base)[0])
                tree = models.tree
                exporter = JsonExporter(indent=2, sort_keys=True)
                draw_tree(tree)
            list_tree=self.class_list_tree(tree)
            self.list_tree = QTreeView(self)
            fnt = QFont()
            fnt.setPixelSize(15)
            self.list_tree.setFont(fnt)
            root_model = QStandardItemModel()
            self.list_tree.setModel(root_model)
            self._populateTree(list_tree, root_model.invisibleRootItem())

            hlayout = QHBoxLayout()
            vlayout1 = QVBoxLayout()
            widget = QWidget()
            widget.setLayout(hlayout)
            sc = Canvas(self)
            toolbar = NavigationToolbar(sc, self)
            vlayout1.addWidget(toolbar)
            vlayout1.addWidget(sc)
            hlayout.addLayout(vlayout1,stretch=4)
            hlayout.addWidget(self.list_tree,stretch=1)
            self.setCentralWidget(widget)
            opened = True


        if (action.text()=="&Save"):
            format = 'txt'
            initialPath = QDir.currentPath() + "/untitled." + format    
            fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
                    "%s Files (*.%s);;All Files (*)" % (format.upper(), format))
            if fileName:
                file = open(fileName, 'w')
                exporter = JsonExporter(indent=2, sort_keys=True)
                text = exporter.export(tree)
                file.write(text)
                file.close()

        if (action.text()=="Login"):
            self.window_login()


def anytree_to_treelib1():
    # moved to models
    return models.anytree_to_treelib1()

def anytree_to_treelib2():
    return models.anytree_to_treelib2()

def draw_tree(tmp_tree):
    """Delegate to :mod:`ontology_app.viz`."""
    return viz.draw_tree(tmp_tree)

def draw_class(tmp_tree):
    """Delegate to :mod:`ontology_app.viz`."""
    return viz.draw_class(tmp_tree)


def create_ontology_tree(fileName):
    return models.create_ontology_tree(fileName)


def add_elem_list1(tmp_tree, elem_name):
    return models.add_elem_list1(tmp_tree, elem_name)

def add_elem_list2(tmp_tree, elem_name):
    return models.add_elem_list2(tmp_tree, elem_name)


def add_class(tree, class_name, type):
    return models.add_class(tree, class_name, type)

def del_class(tree, class_name):
    return models.del_class(tree, class_name)


def add_elem(tree, class_name, elem_name):
    return models.add_elem(tree, class_name, elem_name)

def del_elem(tree, elem_name):
    return models.del_elem(tree, elem_name)

        
def add_classes_rel(tree, class_name1, rel, class_name2): #Функция добавления отношения между классами
    # relocated to models
    return models.add_classes_rel(tree, class_name1, rel, class_name2)

def add_elements_rel(tree, el_name1, rel, el_name2): #Функция добавления отношения между элементами
    # relocated to models
    return models.add_elements_rel(tree, el_name1, rel, el_name2)

def create_series(tree, element, rel):
    # relocated to models
    return models.create_series(tree, element, rel)

def draw_series(series):
    # relocated to viz
    return viz.draw_series(series)


def main():
    app = QApplication(sys.argv)
    demo = Window()
    demo.show()
    #demo.setEnabled(False)
    #log = LoginWindow()
    #log.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()







