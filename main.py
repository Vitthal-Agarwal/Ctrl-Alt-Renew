# main.py

from data_preparation import prepare_data, train_model, predict_future_usage
from gui import ModernMolecularGUI, QApplication
import threading
import sys

class ComputationManager:
    def __init__(self):
        self.current_calculation = {
            'cycle': 0,
            'molecule': None,
            'status': 'idle'
        }
        self.calculation_history = []
        
    def update_current_calculation(self, cycle, molecule):
        self.current_calculation['cycle'] = cycle
        self.current_calculation['molecule'] = molecule
        
    def add_to_history(self, name, score, date, cpu_time):
        self.calculation_history.append({
            'name': name,
            'score': score,
            'date': date,
            'cpu_time': cpu_time
        })

def main():
    # Step 1: Prepare data and train model
    print("Preparing data and training model...")
    df = prepare_data()
    model = train_model(df)

    # Step 2: Predict future usage
    print("Predicting future usage patterns...")
    future_df = predict_future_usage(model, df)

    # Step 3: Initialize computation manager
    computation_manager = ComputationManager()

    # # Step 4: Start the scheduler in a separate thread
    # print("Starting computation scheduler...")
    # scheduler_thread = threading.Thread(
    #     target=schedule_computations, 
    #     args=(future_df, computation_manager)
    # )
    # scheduler_thread.daemon = True
    # scheduler_thread.start()

    # Step 5: Start the GUI
    print("Launching Molecular Universe interface...")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    gui = ModernMolecularGUI(future_df, computation_manager)
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()