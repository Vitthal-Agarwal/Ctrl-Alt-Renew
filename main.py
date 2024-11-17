# main.py

from data_preparation import prepare_data, train_model, predict_future_usage
from scheduler import schedule_computations
from gui import start_gui
import threading

def main():
    # Step 1: Prepare data and train model
    df = prepare_data()
    model = train_model(df)

    # Step 2: Predict future usage (ensure this predicts for one week)
    future_df = predict_future_usage(model, df)

    # Step 3: Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_computations, args=(future_df,))
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Step 4: Start the GUI
    start_gui(future_df)

if __name__ == '__main__':
    main()