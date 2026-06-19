import shutil
import sys
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from anytree.importer import JsonImporter
from anytree.exporter import JsonExporter                                                                                                           
from anytree import *
from PyQt5 import QtCore as qtc
import matplotlib.pyplot as plt
import json
import networkx as nx
import matplotlib.pyplot as plt; plt.ion()
from networkx.drawing.nx_pydot import graphviz_layout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.uic import loadUi
import os

from generativepy.formulas import rasterise_formula

import graphviz
if hasattr(sys, '_MEIPASS'):
    # Если запущено как exe, корень — это папка с exe
    base_dir = os.path.dirname(sys.executable)
else:
    # Если запуск из Python, корень — папка скрипта
    base_dir = os.path.dirname(os.path.abspath(__file__))

graphviz_bin = os.path.abspath(os.path.join(base_dir, 'vendor', 'graphviz', 'bin'))

system_root = os.environ.get('SystemRoot', 'C:\\Windows')
system32 = os.path.join(system_root, 'System32')

os.environ["PATH"] = f"{graphviz_bin}{os.pathsep}{system32}{os.pathsep}{system_root}"


# Добавляем в PATH
os.environ["PATH"] = graphviz_bin + os.pathsep + os.environ["PATH"]

neato_path = shutil.which("neato")
print(f"neato path: {neato_path}")
if not neato_path:
    print("Error: 'neato' executable not found. Please ensure Graphviz is installed and 'neato' is in your system PATH.")

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


opened = False

class LoginWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setWindowTitle("Log in")
        self.setFixedSize(450, 180)
        self.input_user_name = QLabel(self) #Поля ввода элемента
        self.input_user_name.setText("Login")
        self.input_user_name.setGeometry(125, 10, 100, 100)
        self.user_name = qtw.QLineEdit(self)
        self.user_name.setGeometry(75, 70, 150, 25)
        font = self.user_name.font()
        font.setPointSize(11)
        self.input_password = QLabel(self)
        self.input_password.setText("Password")
        self.input_password.setGeometry(270, 10, 100, 100)
        self.password = qtw.QLineEdit(self)
        self.password.setGeometry(230, 70, 150, 25)
        self.log_in_button=QPushButton(self)
        self.log_in_button.setText("Log in")
        self.log_in_button.setGeometry(180, 110, 100, 25)
        self.log_in_button.clicked.connect(self.confirm)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def confirm(self):  
        login = self.user_name.text()
        password = self.password.text()
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
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(500, 200)
        self.setWindowTitle("Add class")
        self.input_class=qtw.QLabel(self)
        self.input_class.setText("Class name")
        self.input_class.setGeometry(165, 10, 100, 100)
        self.class_name=qtw.QLineEdit(self)
        self.class_name.setGeometry(130, 70, 150, 25)
        self.input_type=qtw.QLabel(self)
        self.input_type.setText("Type")
        self.input_type.setGeometry(310, 10, 60, 100)
        self.class_type = QComboBox(self)
        self.class_type.setGeometry(290, 70, 70, 25)
        self.class_type.addItem("Object")
        self.class_type.addItem("Abstract")
        self.input_class_button=qtw.QPushButton(self)
        self.input_class_button.setText("Add")
        self.input_class_button.setGeometry(200, 110, 100, 25)
        self.input_class_button.clicked.connect(self.confirm)
        self.warning = QLabel(self)        
        self.warning.setGeometry(30, 140, 450, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
    def confirm(self):  
        warning = False
        self.warning.setText("")
        current_class = self.class_name.text()
        if(self.class_type.currentText()== "Object"):
            current_type="object"
        if(self.class_type.currentText()== "Abstract"):
            current_type="abstract"
        for pre, fill, node in RenderTree(tree):
            if node.id == current_class + current_type and "null1" in node.parent.id:
                warning = True
                self.warning.setText("Class with name " + current_class + " already exists in the ontology")
        if not warning:
            add_class(tree, current_class, current_type)
            self.close()
            self.main_window.refresh_tree()

class DelClassWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(400, 200)
        self.setWindowTitle("Delete class")
        self.input_class=qtw.QLabel(self)
        self.input_class.setText("Class name")
        self.input_class.setGeometry(150, 10, 60, 100)
        self.class_name = QComboBox(self)
        self.class_name.setGeometry(120, 70, 150, 25)
        self.class_name.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_name.addItem(node.name)
        self.input_type=qtw.QLabel(self)
        self.del_class_button=qtw.QPushButton(self)
        self.del_class_button.setText("Delete")
        self.del_class_button.setGeometry(145, 110, 100, 25)
        self.del_class_button.clicked.connect(self.confirm)
        self.warning = QLabel(self)  
        self.warning.setGeometry(10, 140, 330, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
    def confirm(self):  
        warning = False
        self.warning.setText("")
        current_class = self.class_name.currentText()
        count = 0
        for pre, fill, node in RenderTree(tree):
            if  (node.id == current_class + "object" or node.id == current_class + "abstract") and "null1" in node.parent.id:
                count += 1
        if count == 0:
            warning = True
            self.warning.setText("Class with name " + current_class + " doesn't exist in the ontology")
        if not warning:
            del_class(tree, current_class)
            self.close()
            self.main_window.refresh_tree()  

class AddElemWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(490, 200)
        self.setWindowTitle("Add element")
        self.input_class_of_elem = QLabel(self)
        self.input_class_of_elem.setText("Class name")
        self.input_class_of_elem.setGeometry(125, 10, 100, 100)
        self.elem_class = QComboBox(self)
        self.elem_class.setGeometry(85, 70, 150, 25)
        self.elem_class.setEditable(True)
        font = self.elem_class.font()
        font.setPointSize(11)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.elem_class.addItem(node.name)
        self.input_elem = QLabel(self)
        self.input_elem.setText("Element name")
        self.input_elem.setGeometry(260, 10, 100, 100)
        self.elem_name = qtw.QLineEdit(self)
        self.elem_name.setGeometry(240, 70, 150, 25)
        self.input_elem_button=QPushButton(self)
        self.input_elem_button.setText("Add")
        self.input_elem_button.setGeometry(190, 110, 100, 25)
        self.input_elem_button.clicked.connect(self.confirm)
        self.warning = QLabel(self)  
        self.warning.setGeometry(10, 140, 480, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.elem_class.activated[int].connect(self.class_choosen)

    def class_choosen(self):
        current_class = self.elem_class.currentText()
        for pre, fill, node in RenderTree(tree):
            if current_class + "abstract" == node.id:
                self.abstract_class_window = AddElemWindowAbstract(current_class,"", "", "")
                self.abstract_class_window.show()
                self.close()

    def confirm(self): 
        warning = False
        self.warning.setText("")
        current_class = self.elem_class.currentText()
        current_elem = self.elem_name.text()
        self.elem_name.setText("")
        count = 0
        for pre, fill, node in RenderTree(tree):
            if (current_class == node.name and "null1" in node.parent.id):
                count += 1
        if count == 0:
            warning = True
            self.warning.setText("Class " + current_class + ", to which you want to add an element is not present in the ontology")
        
        count = 0
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_elem + current_class and "null3" in node.parent.id):
                count += 1
        if (count > 0):
            warning = True
            self.warning.setText("Element " + current_elem + " already exists in the ontology for class " + current_class)
        if not warning:
            add_elem(tree, current_class, current_elem)
            self.close()
            self.main_window.refresh_tree()

class AddElemWindowAbstract(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, abstract_class, current_class, current_elem, current_node, parent=None):
        super().__init__(parent)
        self.setFixedSize(1250, 700)
        models.abstract = None
        self.abstract_class = abstract_class
        self.current_class = current_class
        self.current_elem = current_elem
        self.current_node = current_node
        self.setWindowTitle("Add element for abstract class " + abstract_class)
        self.main_elem_name = QLabel(self)
        self.main_elem_name.setText("You are currently working with element: "+ current_elem)
        self.main_elem_name.setGeometry(780, 0, 400, 50)
        self.main_elem_name.setObjectName("HeaderLabel")

        self.input_class_of_elem = QLabel(self) #Поля ввода предметного класса
        self.input_class_of_elem.setText("Object class name")
        self.input_class_of_elem.setGeometry(835, 50, 140, 20)
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
        self.input_main_elem.setGeometry(1005, 50, 100, 20)
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
        self.input_pair.setGeometry(840, 160, 400, 50)
        self.input_pair.setObjectName("HeaderLabel")

        self.input_class_for_elem1 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem1.setText("First class name")
        self.input_class_for_elem1.setGeometry(760, 200, 120, 20)
        self.class_for_elem1_triple = QComboBox(self)
        self.class_for_elem1_triple.setGeometry(745, 220, 150, 25)
        self.class_for_elem1_triple.setEditable(True)
        self.input_class_for_elem2 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem2.setText("Second class name")
        self.input_class_for_elem2.setGeometry(1065, 200, 130, 20)
        self.class_for_elem2_triple = QComboBox(self)
        self.class_for_elem2_triple.setGeometry(1055, 220, 150, 25)
        self.class_for_elem2_triple.setEditable(True)

        self.input_elem1 = QLabel(self) #Поля ввода элемента
        self.input_elem1.setText("First element name")
        self.input_elem1.setGeometry(755, 260, 140, 20)
        self.elem1_tiple = QComboBox(self)
        self.elem1_tiple.setGeometry(745, 280, 150, 25)
        self.elem1_tiple.setEditable(True)
        self.input_rel_triple = QLabel(self) #Поля ввода отношения
        self.input_rel_triple.setText("Relationship name")
        self.input_rel_triple.setGeometry(910, 260, 130, 20)
        self.rel_triple = QLineEdit(self)
        self.rel_triple.setGeometry(900, 280, 150, 25)
        self.input_elem2 = QLabel(self) #Поля ввода элемента
        self.input_elem2.setText("Second element name")
        self.input_elem2.setGeometry(1055, 260, 150, 20)
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
        self.input_one_elem.setGeometry(825, 380, 400, 50)
        self.input_one_elem.setObjectName("HeaderLabel")

        self.input_class_for_elem = QLabel(self) 
        self.input_class_for_elem.setText("Class name")
        self.input_class_for_elem.setGeometry(860, 430, 120, 20)
        self.class_for_elem_one = QComboBox(self)
        self.class_for_elem_one.setGeometry(820, 450, 150, 25)
        self.class_for_elem_one.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_for_elem_one.addItem(node.name)

        self.input_elem = QLabel(self)
        self.input_elem.setText("Element name")
        self.input_elem.setGeometry(1010, 430, 100, 20)
        self.elem_one = QComboBox(self)
        self.elem_one.setGeometry(980, 450, 150, 25)
        self.elem_one.setEditable(True)
        self.class_for_elem_one.activated[int].connect(self.class_choosen_one)

        self.button_add_elem = QPushButton(self)
        self.button_add_elem.setText("Add element")
        self.button_add_elem.setGeometry(925, 490, 100, 25)
        self.button_add_elem.clicked.connect(self.add_elem)

        self.button_arrow_up = QPushButton(self)
        self.button_arrow_up.setText("↑")
        self.button_arrow_up.setGeometry(705, 600, 35, 45)
        self.button_arrow_up.clicked.connect(self.arrow_up)
        self.button_arrow_up.setFont(QFont('Arial', 16, QFont.Bold))

        self.button_arrow_down = QPushButton(self)
        self.button_arrow_down.setText("↓")
        self.button_arrow_down.setGeometry(705, 650, 35, 45)
        self.button_arrow_down.clicked.connect(self.arrow_down)
        self.button_arrow_down.setFont(QFont('Arial', 16, QFont.Bold))

        self.edit_button = QPushButton(self)
        self.edit_button.setText("Edit node")
        self.edit_button.setGeometry(750, 640, 100, 25)
        self.edit_button.clicked.connect(self.edit_elem)

        self.del_button = QPushButton(self)
        self.del_button.setText("Delete node")
        self.del_button.setGeometry(860, 640, 100, 25)
        self.del_button.clicked.connect(self.del_elem)

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
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.main_elem.addItem(node.name)
        self.main_elem.setCurrentText(current_elem)
    
    def class1_choosen_triple(self): #Вывод списка эл первого класса
        self.elem1_tiple.clear()
        current_class = self.class_for_elem1_triple.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem1_tiple.addItem(node.name)
        
    def class2_choosen_triple(self): #Вывод списка элементов второго класса
        self.elem2_triple.clear()
        current_class = self.class_for_elem2_triple.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem2_triple.addItem(node.name)

    def class_choosen_one(self):
        self.elem_one.clear()
        current_class = self.class_for_elem_one.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem_one.addItem(node.name)

    def arrow_up(self):
        cur = ""
        for pre, fill, node in RenderTree(models.abstract):
            if node.id != "root_relation":
                if node.id == self.current_node and "null6" in node.parent.id:
                    cur = node.parent.id
        if cur != "":
            self.current_node = cur
        self.refresh_canvas()

    def arrow_down(self):
        cur = ""
        for pre, fill, node in RenderTree(models.abstract):
            if node.id != "root_relation":
                if node.parent.id == self.current_node and "null6" in node.id:
                    cur = node.id
        if cur != "":
            self.current_node = cur
        self.refresh_canvas()

    def load_elem(self):
        models.abstract = models.create_abstract_class(models.abstract, "load", self.main_elem.currentText(), "", "", "", "", self.current_node)
        cur = ""
        for pre, fill, node in RenderTree(models.abstract):
                if self.main_elem.currentText() + "null6" == node.id:
                    cur = node.id
        self.current_node = cur
        self.current_class = self.class_of_main_elem.currentText()
        self.current_elem = self.main_elem.currentText()
        self.main_elem_name.setText("You are currently working with element: " + self.current_elem)
        self.refresh_canvas()

    def add_triple(self):
        models.abstract = models.create_abstract_class(models.abstract, "add RDF triple", self.main_elem.currentText(), self.elem1_tiple.currentText(), self.elem2_triple.currentText(), self.rel_triple.text(), "", self.current_node)
        self.class_for_elem1_triple.setCurrentText("")
        self.class_for_elem2_triple.setCurrentText("")
        self.elem1_tiple.clear()
        self.elem2_triple.clear()
        self.rel_triple.clear()
        self.refresh_canvas()

    def add_elem(self):
        models.abstract = models.create_abstract_class(models.abstract, "add element", self.main_elem.currentText(), "", "", "", self.elem_one.currentText(), self.current_node)
        self.class_for_elem_one.setCurrentText("")
        self.elem_one.clear()
        self.refresh_canvas()

    def edit_elem(self):
        tmp_node = None
        for pre, fill, node in RenderTree(models.abstract):
            if node.id != "root_relation":
                if node.parent.id == self.current_node:
                    tmp_node = node
        count_nodes = 0
        if tmp_node is not None:
            for pre, fill, node in RenderTree(tmp_node):
                count_nodes += 1
        if count_nodes == 3:
            self.edit_elem_window = EditAbstractStructureTripleWindow(tmp_node, self.current_node, self)
            self.edit_elem_window.show()
        if count_nodes == 1:
            self.edit_elem_window = EditAbstractStructureOneElemWindow(tmp_node, self.current_node, self)
            self.edit_elem_window.show()

    def del_elem(self):
        node_to_delete = None
        for pre, fill, node in RenderTree(models.abstract):
            if node.id == self.current_node:
                node_to_delete = node
        if len(node_to_delete.children) > 0:
            tmp_current_node = self.current_node
            cur = ""
            for pre, fill, node in RenderTree(models.abstract):
                if node.id != "root_relation":
                    if node.parent.id == self.current_node and "null6" in node.id:
                        cur = node.id
            self.current_node = cur
            models.abstract = models.create_abstract_class(models.abstract, "delete", self.main_elem.currentText(), "", "", "", "", tmp_current_node)
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
        if abstract is not None:
            viz.draw_abstract_class(abstract, current_node)
            plt.tight_layout()
        plt.close()

class EditAbstractStructureTripleWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, tmp_node, current_node, abstract_class_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit RDF triple")
        self.current_node = current_node
        self.abstract_class_window = abstract_class_window

        triple = []
        for pre, fill, node in RenderTree(tmp_node):
            triple.append(node.name)

        self.input_class_for_elem1 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem1.setText("First class name")
        self.input_class_for_elem1.setGeometry(100, 50, 100, 20)
        self.class_for_elem1_triple = QComboBox(self)
        self.class_for_elem1_triple.setGeometry(70, 70, 150, 25)
        self.class_for_elem1_triple.setEditable(True)
        self.input_class_for_elem2 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem2.setText("Second class name")
        self.input_class_for_elem2.setGeometry(435, 50, 100, 20)
        self.class_for_elem2_triple = QComboBox(self)
        self.class_for_elem2_triple.setGeometry(415, 70, 150, 25)
        self.class_for_elem2_triple.setEditable(True)

        self.input_elem1 = QLabel(self) #Поля ввода элемента
        self.input_elem1.setText("First element name")
        self.input_elem1.setGeometry(90, 110, 120, 20)
        self.elem1_tiple = QComboBox(self)
        self.elem1_tiple.setGeometry(70, 130, 150, 25)
        self.elem1_tiple.setEditable(True)
        self.input_rel_triple = QLabel(self) #Поля ввода отношения
        self.input_rel_triple.setText("Relationship name")
        self.input_rel_triple.setGeometry(260, 110, 100, 20)
        self.rel_triple = QLineEdit(self)
        self.rel_triple.setGeometry(240, 130, 150, 25)
        self.input_elem2 = QLabel(self) #Поля ввода элемента
        self.input_elem2.setText("Second element name")
        self.input_elem2.setGeometry(445, 110, 120, 20)
        self.elem2_triple = QComboBox(self)
        self.elem2_triple.setGeometry(415, 130, 150, 25)
        self.elem2_triple.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_for_elem1_triple.addItem(node.name)
                    self.class_for_elem2_triple.addItem(node.name)
        self.class_for_elem1_triple.setCurrentText("")
        self.class_for_elem2_triple.setCurrentText("")
        self.elem1_tiple.setCurrentText(triple[1])
        self.rel_triple.setText(triple[0])
        self.elem2_triple.setCurrentText(triple[2])
        self.button_save=QPushButton(self)
        self.button_save.setText("Save")
        self.button_save.setGeometry(260, 170, 100, 25)
        self.button_save.clicked.connect(self.save_triple)
        self.class_for_elem1_triple.activated[int].connect(self.class1_choosen_triple)
        self.class_for_elem2_triple.activated[int].connect(self.class2_choosen_triple)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def class1_choosen_triple(self): #Вывод списка эл первого класса
        self.elem1_tiple.clear()
        current_class = self.class_for_elem1_triple.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem1_tiple.addItem(node.name)
        
    def class2_choosen_triple(self): #Вывод списка элементов второго класса
        self.elem2_triple.clear()
        current_class = self.class_for_elem2_triple.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem2_triple.addItem(node.name)

    def save_triple(self):
        models.abstract = models.create_abstract_class(models.abstract, "edit RDF triple", "", self.elem1_tiple.currentText(), self.elem2_triple.currentText(), self.rel_triple.text(), "", self.current_node)
        self.close()
        self.abstract_class_window.refresh_canvas()

class EditAbstractStructureOneElemWindow(qtw.QWidget):
    def __init__(self, tmp_node, current_node, abstract_class_window, parent=None):
        super().__init__(parent)
        self.current_node = current_node
        self.abstract_class_window = abstract_class_window
        self.input_class_for_elem = QLabel(self) 
        self.input_class_for_elem.setText("Class name")
        self.input_class_for_elem.setGeometry(110, 50, 100, 20)
        self.class_for_elem_one = QComboBox(self)
        self.class_for_elem_one.setGeometry(70, 70, 150, 25)
        self.class_for_elem_one.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_for_elem_one.addItem(node.name)
        self.class_for_elem_one.setCurrentText("")
        self.input_elem = QLabel(self)
        self.input_elem.setText("Element name")
        self.input_elem.setGeometry(280, 50, 100, 20)
        self.elem_one = QComboBox(self)
        self.elem_one.setGeometry(240, 70, 150, 25)
        self.elem_one.setEditable(True)
        self.elem_one.setCurrentText(tmp_node.name)
        self.class_for_elem_one.activated[int].connect(self.class_choosen_one)

        self.button_save_elem = QPushButton(self)
        self.button_save_elem.setText("Save element")
        self.button_save_elem.setGeometry(170, 110, 100, 25)
        self.button_save_elem.clicked.connect(self.save_elem)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def class_choosen_one(self):
        self.elem_one.clear()
        current_class = self.class_for_elem_one.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem_one.addItem(node.name)

    def save_elem(self):
        models.abstract = models.create_abstract_class(models.abstract, "edit one element", "", "", "", "", self.elem_one.currentText(), self.current_node)
        self.close()
        self.abstract_class_window.refresh_canvas()

class DelElemWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete element")
        self.input_class_of_elem = QLabel(self) 
        self.input_class_of_elem.setText("Class name")
        self.input_class_of_elem.setGeometry(125, 10, 100, 100)
        self.elem_class = QComboBox(self)
        self.elem_class.setGeometry(75, 70, 150, 25)
        self.elem_class.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.elem_class.addItem(node.name)

        self.input_elem = QLabel(self)
        self.input_elem.setText("Element name")
        self.input_elem.setGeometry(270, 10, 100, 100)
        self.elem_name = QComboBox(self)
        self.elem_name.setEditable(True)
        self.elem_name.setGeometry(230, 70, 150, 25)
        self.del_elem_button=QPushButton(self)
        self.del_elem_button.setText("Delete")
        self.del_elem_button.setGeometry(175, 100, 100, 25)
        self.del_elem_button.clicked.connect(self.confirm)
        self.space = QLabel(self)
        self.space.setGeometry(175, 140, 100, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.elem_class.activated[int].connect(self.class_choosen)

    def class_choosen(self): #Вывод списка эл класса
        self.elem_name.clear()
        current_class = self.elem_class.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem_name.addItem(node.name)
        
    def confirm(self): 
        warning = False
        self.warning.setText("")
        current_class = self.elem_class.currentText()
        current_elem = self.elem_name.text()
        self.elem_name.setText("")
        count = 0
        for pre, fill, node in RenderTree(tree):
            if (current_class == node.name and "null1" in node.parent.id):
                count += 1
        if count == 0:
            warning = True
            self.warning.setText("Class " + current_class + ", to which you want to add an element is not present in the ontology")
        
        count = 0
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_elem + current_class and "null3" in node.parent.id):
                count += 1
        if (count == 0):
            warning = True
            self.warning.setText("Element " + current_elem + " does not exist in the ontology for class " + current_class)
        if not warning:
            del_elem(tree, current_class, current_elem)
            self.close()
            self.main_window.refresh_tree()

class AddRelClassesWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(620, 200)
        self.setWindowTitle("Add relationships between classes")
        self.input_class1 = QLabel(self) #Поля ввода класса
        self.input_class1.setText("First class name")
        self.input_class1.setGeometry(120, 10, 100, 100)
        self.class1 = QComboBox(self)
        self.class1.setGeometry(95, 70, 150, 25)
        self.class1.setEditable(True)
        self.input_rel = QLabel(self) 
        self.input_rel.setText("Relationship name")
        self.input_rel.setGeometry(290, 10, 100, 100)
        self.rel = QLineEdit(self)
        self.rel.setGeometry(250, 70, 150, 25)
        self.input_class2 = QLabel(self) #Поля ввода класса
        self.input_class2.setText("Second class name")
        self.input_class2.setGeometry(435, 10, 100, 100)
        self.class2 = QComboBox(self)
        self.class2.setGeometry(405, 70, 150, 25)
        self.class2.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class1.addItem(node.name)
                    self.class2.addItem(node.name)
        self.add_rel_classes_button=QPushButton(self)
        self.add_rel_classes_button.setText("Add")
        self.add_rel_classes_button.setGeometry(275, 110, 100, 25)
        self.add_rel_classes_button.clicked.connect(self.confirm)
        self.warning = QLabel(self)
        self.warning.setGeometry(10, 140, 600, 25)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
    def confirm(self): 
        warning = False
        self.warning.setText("")
        current_class1 = self.class1.currentText()
        current_rel = self.rel.text()
        current_class2 = self.class2.currentText()
        self.rel.setText("")
        count1=0
        count2=0
        for pre, fill, node in RenderTree(tree):
            if (current_class1 + "object" == node.id and "null1" in node.parent.id):
                count1=count1+1
            if (current_class2 + "object" == node.id and "null1" in node.parent.id):
                count2=count2+1
        if (count1==0 and count2!=0):
            warning = True
            self.warning.setText("Class " + current_class1 + " is not present in the ontology")
        if (count2==0 and count1!=0):
            warning = True
            self.warning.setText("Class " + current_class2 + " is not present in the ontology")
        if (count2==0 and count1==0):
            warning = True
            self.warning.setText("Classes " + current_class1 + " and " + current_class2 + " are not present in the ontology")

        if not warning:
            add_classes_rel(tree, current_class1, current_rel, current_class2)
            self.close()
            self.main_window.refresh_tree()

class AddRelElemWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(1250, 700)
        self.setWindowTitle("Add relationships between elements")
        self.input_class_for_elem1 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem1.setText("First class name")
        self.input_class_for_elem1.setGeometry(760, 20, 120, 30)
        self.class1 = QComboBox(self)
        self.class1.setGeometry(745, 50, 150, 25)
        self.class1.setEditable(True)
        self.input_class_for_elem2 = QLabel(self) #Поля ввода класса
        self.input_class_for_elem2.setText("Second class name")
        self.input_class_for_elem2.setGeometry(1065, 20, 130, 30)
        self.class2 = QComboBox(self)
        self.class2.setGeometry(1055, 50, 150, 25)
        self.class2.setEditable(True)

        self.input_elem1 = QLabel(self) #Поля ввода элемента
        self.input_elem1.setText("First element name")
        self.input_elem1.setGeometry(755, 100, 140, 30)
        self.elem1 = QComboBox(self)
        self.elem1.setGeometry(745, 130, 150, 25)
        self.elem1.setEditable(True)
        self.input_rel = QLabel(self) #Поля ввода отношения
        self.input_rel.setText("Relationship name")
        self.input_rel.setGeometry(910, 100, 130, 30)
        self.rel = QLineEdit(self)
        self.rel.setGeometry(900, 130, 150, 25)
        self.input_elem2 = QLabel(self) #Поля ввода элемента
        self.input_elem2.setText("Second element name")
        self.input_elem2.setGeometry(1055, 100, 160, 30)
        self.elem2 = QComboBox(self)
        self.elem2.setGeometry(1055, 130, 150, 25)
        self.elem2.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class1.addItem(node.name)
                    self.class2.addItem(node.name)
        self.add_elem_rel_button=QPushButton(self)
        self.add_elem_rel_button.setText("Add")
        self.add_elem_rel_button.setGeometry(925, 180, 100, 25)
        self.add_elem_rel_button.clicked.connect(self.add)
        self.warning = QLabel(self)
        self.warning.setGeometry(770, 220, 400, 25)
        self.class1.activated[int].connect(self.class1_choosen)
        self.class2.activated[int].connect(self.class2_choosen)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        self.sc = CanvasElemChoosen(self, "", "")
        self.hlayout = QHBoxLayout()
        self.vlayout1 = QVBoxLayout()
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.hlayout.addLayout(self.vlayout1)
        self.widget = QWidget(self)
        self.widget.setGeometry(0, 0, 700, 700)
        self.widget.setLayout(self.hlayout)

    def refresh_canvas(self, current_class_1, current_class_2):
        self.vlayout1.removeWidget(self.toolbar)
        self.vlayout1.removeWidget(self.sc)
        self.toolbar.setParent(None)
        self.sc.setParent(None)
        self.toolbar.deleteLater()
        self.sc.deleteLater()
        self.sc = CanvasElemChoosen(self, current_class_1, current_class_2)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.update()
    
    def class1_choosen(self): #Вывод списка эл первого класса
        self.elem1.clear()
        current_class_1 = self.class1.currentText()
        current_class_2 = self.class2.currentText()
        self.refresh_canvas(current_class_1, current_class_2)
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class_1 + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class_1 and node.name+current_class_1 == node.id):
                    self.elem1.addItem(node.name)
        

    def class2_choosen(self): #Вывод списка элементов второго класса
        self.elem2.clear()
        current_class_1 = self.class1.currentText()
        current_class_2 = self.class2.currentText()
        self.refresh_canvas(current_class_1, current_class_2)
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class_2 + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class_2 and node.name+current_class_2 == node.id):
                    self.elem2.addItem(node.name)
       
    def add(self):
        warning = False
        self.warning.setText("")
        current_elem1 = self.elem1.currentText()
        current_rel = self.rel.text()
        current_elem2 = self.elem2.currentText()
        self.rel.setText("")
        count1=0
        count2=0
        for pre, fill, node1 in RenderTree(tree):
            if (node1.id != "Null"):
                if "null1" in node1.parent.id:
                    for pre, fill, node2 in RenderTree(tree):
                        if current_elem1+node1.name == node2.id:
                            count1=count1+1
                        if current_elem2+node1.name == node2.id:
                            count2=count2+1
        if (count1==0 and count2!=0):
            warning = True
            self.warning.setText("Element " + current_elem1 + " is not present in the ontology")
        if (count2==0 and count1!=0):
            warning = True
            self.warning.setText("Element " + current_elem2 + " is not present in the ontology")
        if (count2==0 and count1==0):
            warning = True
            self.warning.setText("Elements " + current_elem1 + " and " + current_elem2 + " are not present in the ontology")

        if not warning:
            add_elements_rel(tree, current_elem1, current_rel, current_elem2)
            self.refresh_canvas(self.class1.currentText(), self.class2.currentText())
            #self.close()
            #self.main_window.refresh_tree()

class CreateNeighborhoodWindow(qtw.QWidget):
    submitClicked = qtc.pyqtSignal(str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(200,200,1250,700)
        self.setWindowTitle("Create a knowledge neighborhood")
        models.series = None

        self.series_depth_1 = QLabel(self)
        self.series_depth_1.setText("Create a series of depth 1:")
        self.series_depth_1.setGeometry(850, 60, 400, 50)
        self.series_depth_1.setFont(QFont('Arial', 12))
        self.series_depth_1.setObjectName("HeaderLabel")

        self.input_class_depth_1 = QLabel(self) #Поле ввода класса
        self.input_class_depth_1.setText("Class name")
        self.input_class_depth_1.setGeometry(775, 100, 120, 30)
        self.class_name_depth_1 = QComboBox(self)
        self.class_name_depth_1.setGeometry(745, 130, 150, 25)
        self.class_name_depth_1.setEditable(True)

        self.input_elem_depth_1 = QLabel(self) #Поле ввода элемента
        self.input_elem_depth_1.setText("Element name")
        self.input_elem_depth_1.setGeometry(920, 100, 100, 30)
        self.elem_name_depth_1 = QComboBox(self)
        self.elem_name_depth_1.setGeometry(900, 130, 150, 25)
        self.elem_name_depth_1.setEditable(True)
        self.input_rel_depth_1 = QLabel(self) #Поле ввода отношения
        self.input_rel_depth_1.setText("Relationship name")
        self.input_rel_depth_1.setGeometry(1065, 100, 140, 30)
        self.rel_name_depth_1 = QComboBox(self)
        self.rel_name_depth_1.setGeometry(1055, 130, 150, 25)
        self.rel_name_depth_1.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_name_depth_1.addItem(node.name)
        for pre, fill, node in RenderTree(tree):
                if (node.id != "Null"):
                    if (node.name!="•" and node.name + " in elements" + "null4" == node.id and "null4" in node.parent.id):
                        self.rel_name_depth_1.addItem(node.name)
        self.rel_name_depth_1.setCurrentText("")
        self.create_series_depth_1_button=QPushButton(self)
        self.create_series_depth_1_button.setText("Create")
        self.create_series_depth_1_button.setGeometry(925, 170, 100, 25)
        self.create_series_depth_1_button.clicked.connect(self.create_depth_1)
        self.space = QLabel(self)
        self.space.setGeometry(825, 190, 100, 25)
        self.class_name_depth_1.activated[int].connect(self.class_choosen_depth_1)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.series_depth_2 = QLabel(self)
        self.series_depth_2.setText("Create a series of depth 2:")
        self.series_depth_2.setGeometry(850, 220, 400, 50)
        self.series_depth_2.setFont(QFont('Arial', 12))
        self.series_depth_2.setObjectName("HeaderLabel")

        self.input_class_depth_2 = QLabel(self) #Поле ввода класса
        self.input_class_depth_2.setText("Class name")
        self.input_class_depth_2.setGeometry(775, 260, 120, 30)
        self.class_name_depth_2 = QComboBox(self)
        self.class_name_depth_2.setGeometry(745, 290, 150, 25)
        self.class_name_depth_2.setEditable(True)
        self.input_elem_depth_2 = QLabel(self) #Поле ввода элемента
        self.input_elem_depth_2.setText("Element name")
        self.input_elem_depth_2.setGeometry(775, 320, 100, 30)
        self.elem_name_depth_2 = QComboBox(self)
        self.elem_name_depth_2.setGeometry(745, 350, 150, 25)
        self.elem_name_depth_2.setEditable(True)

        self.input_rel_1_depth_2 = QLabel(self) 
        self.input_rel_1_depth_2.setText("Relationship name 1")
        self.input_rel_1_depth_2.setGeometry(900, 260, 150, 30)
        self.rel_name_1_depth_2 = QComboBox(self)
        self.rel_name_1_depth_2.setGeometry(900, 290, 150, 25)
        self.input_rel_2_depth_2 = QLabel(self) #Поле ввода отношения
        self.input_rel_2_depth_2.setText("Relationship name 2")
        self.input_rel_2_depth_2.setGeometry(1055, 260, 150, 30)
        self.rel_name_2_depth_2 = QComboBox(self)
        self.rel_name_2_depth_2.setGeometry(1055, 290, 150, 25)
        self.rel_name_1_depth_2.setEditable(True)
        self.rel_name_2_depth_2.setEditable(True)
        for pre, fill, node in RenderTree(tree):
            if (node.id!="Null"):
                if (node.name!="•" and "null1" in node.parent.id):
                    self.class_name_depth_2.addItem(node.name)
        for pre, fill, node in RenderTree(tree):
                if (node.id != "Null"):
                    if (node.name!="•" and node.name + " in elements" + "null4" == node.id and "null4" in node.parent.id):
                        self.rel_name_2_depth_2.addItem(node.name)
                        self.rel_name_1_depth_2.addItem(node.name)
        self.rel_name_1_depth_2.setCurrentText("")
        self.rel_name_2_depth_2.setCurrentText("")
        self.create_series_depth_2_button=QPushButton(self)
        self.create_series_depth_2_button.setText("Create")
        self.create_series_depth_2_button.setGeometry(925, 380, 100, 25)
        self.create_series_depth_2_button.clicked.connect(self.create_depth_2)
        self.class_name_depth_2.activated[int].connect(self.class_choosen_depth_2)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        self.sc = CanvasSeries(self, self.rel_name_1_depth_2.currentText(), "", 0)
        self.hlayout = QHBoxLayout()
        self.vlayout1 = QVBoxLayout()
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.hlayout.addLayout(self.vlayout1)
        self.widget = QWidget(self)
        self.widget.setGeometry(0, 0, 700, 700)
        self.widget.setLayout(self.hlayout)

    def refresh_canvas(self, depth):
        self.vlayout1.removeWidget(self.toolbar)
        self.vlayout1.removeWidget(self.sc)
        self.toolbar.setParent(None)
        self.sc.setParent(None)
        self.toolbar.deleteLater()
        self.sc.deleteLater()
        if self.rel_name_1_depth_2.currentText()!="" and self.rel_name_2_depth_2.currentText()!="":
            self.sc = CanvasSeries(self, self.rel_name_1_depth_2.currentText(), self.elem_name_depth_2.currentText(), depth)
        if self.rel_name_depth_1.currentText()!="":
            self.sc = CanvasSeries(self, self.rel_name_depth_1.currentText(), self.elem_name_depth_1.currentText(), depth)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vlayout1.addWidget(self.toolbar)
        self.vlayout1.addWidget(self.sc)
        self.update()

    def class_choosen_depth_1(self): #Вывод списка элементов класса
        self.elem_name_depth_1.clear()
        current_class = self.class_name_depth_1.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem_name_depth_1.addItem(node.name)

    def class_choosen_depth_2(self): #Вывод списка элементов класса
        self.elem_name_depth_2.clear()
        current_class = self.class_name_depth_2.currentText()
        node_class = None
        for pre, fill, node in RenderTree(tree):
            if (node.id == current_class + " in elements" + "null3"):
                node_class = node.parent
        if (node_class is not None):
            for pre, fill, node in RenderTree(tree):
                if (node.name!="•" and node.name!=current_class and node.name+current_class == node.id):
                    self.elem_name_depth_2.addItem(node.name)
            
    def create_depth_1(self):
        models.series = create_series(tree, models.series, "1", self.elem_name_depth_1.currentText(), self.rel_name_depth_1.currentText(), "", 0)
        self.refresh_canvas(1)
        self.elem_name_depth_1.setCurrentText("")
        self.rel_name_depth_1.setCurrentText("")
    
    def create_depth_2(self):
        models.series = create_series(tree, models.series, "2", self.elem_name_depth_2.currentText(), self.rel_name_1_depth_2.currentText(), self.rel_name_2_depth_2.currentText(), 0)
        self.refresh_canvas(2)
        self.elem_name_depth_2.setCurrentText("")
        self.rel_name_1_depth_2.setCurrentText("")
        self.rel_name_2_depth_2.setCurrentText("")

class CanvasSeries(FigureCanvasQTAgg):
    def __init__(self, parent, rel, element, depth):
        fig, self.ax = plt.subplots(figsize=(7, 7))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        super(CanvasSeries, self).__init__(fig)
        self.setParent(parent)
        series = models.series
        if series is not None:
            if depth == 1:
                viz.draw_series_depth_1(series, rel, element)
            elif depth == 2:
                viz.draw_series_depth_2(series, rel)
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
    def __init__(self, parent, current_class_1, current_class_2):
        fig, self.ax = plt.subplots(figsize=(7, 7))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        super(CanvasElemChoosen, self).__init__(fig)
        self.setParent(parent)
        draw_class(tree, current_class_1, current_class_2)
        plt.close()

class Window(QMainWindow, QDialog):
    #resized = QtCore.pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Ontology ")
        self.initUI()

    def initUI(self):
        QWidget.__init__(self)
        tree = {}
        self.tree = QTreeView(self)
        root_model = QStandardItemModel()
        self.tree.setModel(root_model)
        self._populateTree(tree, root_model.invisibleRootItem())
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        #width = self.frameGeometry().width()
        #self.resized.connect(self.resize)

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

        button_create_series = QAction("Create a knowledge neighborhood", self)
        button_create_series.setFont(QFont('Times', 10))
        button_create_series.triggered.connect(self.window_create_neighborhood)
        toolbar.addAction(button_create_series)

        self.resize(1400, 800)


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
                            if (node.id == current_class + " in elements" + "null3"):
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
        fileMenu.addAction(loginAction)
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)
        fileMenu.triggered[QAction].connect(self.do_something_ontology)

    def window_login(self):
        self.login_window = LoginWindow()
        self.login_window.submitClicked.connect(self.login_clicked)
        self.login_window.show()


    def window_add_class(self):
        if opened:
            self.add_class_window = AddClassWindow(self)
            self.add_class_window.class_name.setText("")
            self.add_class_window.show()

    def window_del_class(self):
        if opened:
            self.del_class_window = DelClassWindow(self)
            self.del_class_window.show()

    def window_add_elem(self):
        if opened:
            self.add_elem_window = AddElemWindow(self)
            self.add_elem_window.elem_name.setText("")
            self.add_elem_window.show()

    def window_del_elem(self):
        if opened:
            self.del_elem_window = DelElemWindow(self)
            self.del_elem_window.show()

    def window_add_rel_classes(self):
        if opened:
            self.add_rel_classes_window = AddRelClassesWindow(self)
            self.add_rel_classes_window.rel.setText("")
            self.add_rel_classes_window.show()
    
    def window_add_rel_elem(self):
        if opened:
            self.add_rel_elem_window = AddRelElemWindow(self)
            self.add_rel_elem_window.rel.setText("")
            self.add_rel_elem_window.show()

    def window_create_neighborhood(self):
        if opened:
            self.create_neighborhood_window = CreateNeighborhoodWindow()
            self.create_neighborhood_window.show()

    @pyqtSlot()
    def refresh_tree(self):  
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
                file = open(fileName, 'w')
                exporter = JsonExporter(indent=2, sort_keys=True)
                text = exporter.export(tree)
                file.write(text)
                file.close()
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

def draw_class(tmp_tree, current_class_1, current_class_2):
    """Delegate to :mod:`ontology_app.viz`."""
    return viz.draw_class(tmp_tree, current_class_1, current_class_2)

def create_ontology_tree(fileName):
    return models.create_ontology_tree(fileName)


def add_class(tree, class_name, type):
    return models.add_class(tree, class_name, type)

def del_class(tree, class_name):
    return models.del_class(tree, class_name)


def add_elem(tree, class_name, elem_name):
    return models.add_elem(tree, class_name, elem_name)

def del_elem(tree, elem_name, class_name):
    return models.del_elem(tree, elem_name, class_name)

        
def add_classes_rel(tree, class_name1, rel, class_name2): #Функция добавления отношения между классами
    # relocated to models
    return models.add_classes_rel(tree, class_name1, rel, class_name2)

def add_elements_rel(tree, el_name1, rel, el_name2): #Функция добавления отношения между элементами
    # relocated to models
    return models.add_elements_rel(tree, el_name1, rel, el_name2)

def create_series(tree, series, depth, element, rel, rel_2, count):
    # relocated to models
    return models.create_series(tree, series, depth, element, rel, rel_2, count)

def draw_series(series, rel):
    # relocated to viz
    return viz.draw_series(series, rel)


def load_stylesheet(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet('style.css'))
    demo = Window()
    demo.show()
    demo.setEnabled(False)
    login = LoginWindow(demo)
    login.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()







