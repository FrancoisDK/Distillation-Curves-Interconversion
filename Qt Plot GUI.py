import sys
import csv
import numpy as np
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, QToolBar, QMessageBox, QDialog, QSpinBox, QHBoxLayout
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scipy.interpolate import PchipInterpolator
from openpyxl import Workbook

# Constants
ICON_PATH = Path(__file__).parent / "D86_fancy.png"

def set_colorful_mode():
    plt.style.use('seaborn-colorblind')
    plt.rcParams.update({
        'axes.facecolor': '#EAEAF2',
        'axes.edgecolor': 'black',
        'axes.labelcolor': 'black',
        'xtick.color': 'black',
        'ytick.color': 'black',
        'grid.color': 'gray',
        'figure.facecolor': '#EAEAF2',
        'figure.edgecolor': '#EAEAF2',
        'savefig.facecolor': '#EAEAF2',
        'savefig.edgecolor': '#EAEAF2',
        'text.color': 'black',
        'lines.color': 'black',
        'patch.edgecolor': 'black',
        'patch.facecolor': '#EAEAF2',
    })

def set_normal_mode():
    plt.style.use('default')
    plt.rcParams.update({
        'axes.facecolor': 'white',
        'axes.edgecolor': 'black',
        'axes.labelcolor': 'black',
        'xtick.color': 'black',
        'ytick.color': 'black',
        'grid.color': 'gray',
        'figure.facecolor': 'white',
        'figure.edgecolor': 'white',
        'savefig.facecolor': 'white',
        'savefig.edgecolor': 'white',
        'text.color': 'black',
        'lines.color': 'black',
        'patch.edgecolor': 'black',
        'patch.facecolor': 'white',
    })

class TBPconversions():
    def __init__(self):
        pass
    def tbp_to_astm_d86(self, tbp_data):
       """
       Convert TBP distillation data to ASTM D86.
       Args:
           tbp_data (list of tuples): List of (temperature, volume) tuples representing TBP data.
       Returns:
           list of tuples: List of (temperature, volume) tuples representing ASTM D86 data.
       """
       astm_d86_data = []
       for temp, volume in tbp_data:
           # Example conversion formula (this is a placeholder, actual conversion may vary)
           astm_temp = self.convert_tbp_to_d86(temp)
           astm_d86_data.append((astm_temp, volume))
       return astm_d86_data
    
    def convert_tbp_to_d86(self, tbp_temp):
        """
        Convert a single TBP temperature to ASTM D86 temperature.

        Args:
            tbp_temp (float): TBP temperature.

        Returns:
            float: ASTM D86 temperature.
        """
        # Placeholder conversion formula (actual formula may vary)
        astm_temp = tbp_temp * 0.95 + 5
        return astm_temp
       

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor='#D3D3D3')  # Light gray background
        self.ax = self.fig.add_subplot(111, facecolor='#D3D3D3')  # Light gray background
        super().__init__(self.fig)
        self.setParent(parent)
        self.num_points = 15  # Default number of datapoints for the spline
        self.xlabel = "x"
        self.ylabel = "y"
        self.plot()

    def plot(self, x=None, y=None, xlabel=None, ylabel=None):
        self.ax.clear()
        self.ax.set_facecolor('#D3D3D3')  # Set the axes background color to light gray
        if x is not None and y is not None:
            self.ax.plot(x, y, 'r', linewidth=1.5, label='TBP Data')  # Red color for x and y values
            x_new = np.linspace(min(x), max(x), self.num_points)
            self.ax.xaxis.set_major_locator(plt.MultipleLocator(10))
            self.ax.yaxis.set_major_locator(plt.MultipleLocator(10))
            self.ax.xaxis.set_minor_locator(plt.MultipleLocator(5))
            self.ax.yaxis.set_minor_locator(plt.MultipleLocator(5))
            self.ax.grid(which='minor', linestyle='--', linewidth='0.5', color='blue')
            self.ax.grid(which='major', linestyle='-', linewidth='0.75', color='blue')
            pchip = PchipInterpolator(x, y)
            y_smooth = pchip(x_new)
            self.ax.plot(x_new, y_smooth, 'b--', linewidth=2, label='Spline')  # Dashed line for spline, thicker
            self.spline_x = x_new
            self.spline_y = y_smooth
        if xlabel:
            self.xlabel = xlabel
        if ylabel:
            self.ylabel = ylabel
        self.ax.set_xlabel(self.xlabel, color='black')
        self.ax.set_ylabel(self.ylabel, color='black')
        self.ax.legend(['Data', 'Spline'], facecolor='#D3D3D3', edgecolor='black')
        self.draw()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()

        self.num_points_label = QLabel('Number of datapoints for spline:')
        self.num_points_spinbox = QSpinBox()
        self.num_points_spinbox.setRange(10, 1000)
        self.num_points_spinbox.setValue(parent.canvas.num_points)

        layout.addWidget(self.num_points_label)
        layout.addWidget(self.num_points_spinbox)

        self.button_box = QHBoxLayout()
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        self.button_box.addWidget(self.ok_button)
        self.button_box.addWidget(self.cancel_button)

        layout.addLayout(self.button_box)
        self.setLayout(layout)

    def accept(self):
        parent = self.parent()
        parent.canvas.num_points = self.num_points_spinbox.value()
        parent.canvas.plot(parent.canvas.spline_x, parent.canvas.spline_y, parent.canvas.xlabel, parent.canvas.ylabel)
        super().accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('XY Plotter with Spline')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(str(ICON_PATH)))  # Set the window icon

        self.canvas = PlotCanvas(self)
        self.setCentralWidget(self.canvas)

        # Add the navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.addToolBar(self.toolbar)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        importAction = QAction('Import CSV', self)
        importAction.triggered.connect(self.importCSV)
        fileMenu.addAction(importAction)

        exportAction = QAction('Export Spline to Excel', self)
        exportAction.triggered.connect(self.exportSplineToExcel)
        fileMenu.addAction(exportAction)

        settingsMenu = menubar.addMenu('Settings')
        settingsAction = QAction('Settings', self)
        settingsAction.triggered.connect(self.showSettingsDialog)
        settingsMenu.addAction(settingsAction)

        aboutMenu = menubar.addMenu('Help')
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.showAbout)
        aboutMenu.addAction(aboutAction)

        self.show()

    def importCSV(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            x, y = [], []
            xlabel, ylabel = "x", "y"
            with open(fileName, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                first_row = next(reader)
                try:
                    # Try to convert the first row to floats
                    float(first_row[0])
                    float(first_row[1])
                    # If successful, use the first row as data
                    x.append(float(first_row[0]))
                    y.append(float(first_row[1]))
                except ValueError:
                    # If conversion fails, use the first row as labels
                    xlabel, ylabel = first_row[0], first_row[1]
                for row in reader:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
            self.canvas.plot(x, y, xlabel, ylabel)
            self.canvas.draw()  # Ensure the canvas is updated

    def exportSplineToExcel(self):
        if hasattr(self.canvas, 'spline_x') and hasattr(self.canvas, 'spline_y'):
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Spline Data", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
            if fileName:
                if not fileName.endswith('.xlsx'):
                    fileName += '.xlsx'
                wb = Workbook()
                ws = wb.active
                ws.title = "Spline Data"
                ws.append(["Spline X", "Spline Y"])
                for x, y in zip(self.canvas.spline_x, self.canvas.spline_y):
                    ws.append([x, y])
                try:
                    wb.save(fileName)
                    QMessageBox.information(self, "Export Successful", f"Spline data has been exported to {fileName}")
                except OSError:
                    QMessageBox.warning(self, "File Open Error", f"Cannot write to file {fileName} because it is open. Please close the file and try again.")
        else:
            QMessageBox.warning(self, "No Spline Data", "No spline data available to export.")

    def showSettingsDialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def showAbout(self):
        QMessageBox.about(
            self,
            "About",
            """<h3>XY Plotter with Spline</h3>
            <p>Version 1.0</p>
            <p>Author: F. de Klerk </p>
            <p>Features:</p>
            <ul>
                <li>Import CSV data</li>
                <li>Plot data with spline interpolation</li>
                <li>Export spline data to Excel</li>
                <li>Settings for number of datapoints</li>
            </ul>"""
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON_PATH)))  # Set the application icon
    mainWin = MainWindow()
    mainWin.show()  # Ensure the main window is shown
    sys.exit(app.exec())