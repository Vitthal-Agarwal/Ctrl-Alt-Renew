# scripts/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import time

from simulation import (
    start_high_intensity_computation,
    start_medium_intensity_computation,
    start_low_intensity_computation,
    stop_computation,
)

def schedule_computations(future_df):
    # Initialize the scheduler
    scheduler = BackgroundScheduler()

    # Schedule computations based on predicted status
    for idx, row in future_df.iterrows():
        run_time = row['Timestamp'].to_pydatetime()
        predicted_status = row['Predicted_Status']

        # Create unique job IDs
        job_id_start = f'start_{idx}'
        job_id_stop = f'stop_{idx}'

        computation_duration = datetime.timedelta(minutes=15)
        end_time = run_time + computation_duration

        if predicted_status == 0:  # Idle
            # Schedule high-intensity computation
            scheduler.add_job(start_high_intensity_computation, 'date', run_date=run_time, id=job_id_start)
            scheduler.add_job(stop_computation, 'date', run_date=end_time, id=job_id_stop)
            print(f"Scheduled HIGH-intensity computation from {run_time} to {end_time}")
        elif predicted_status == 1:  # Medium Usage
            # Schedule medium-intensity computation
            scheduler.add_job(start_medium_intensity_computation, 'date', run_date=run_time, id=job_id_start)
            scheduler.add_job(stop_computation, 'date', run_date=end_time, id=job_id_stop)
            print(f"Scheduled MEDIUM-intensity computation from {run_time} to {end_time}")
        elif predicted_status == 2:  # High Usage
            # Schedule low-intensity computation
            scheduler.add_job(start_low_intensity_computation, 'date', run_date=run_time, id=job_id_start)
            scheduler.add_job(stop_computation, 'date', run_date=end_time, id=job_id_stop)
            print(f"Scheduled LOW-intensity computation from {run_time} to {end_time}")
        else:
            # Very High Usage - No computation scheduled
            print(f"No computation scheduled at {run_time} due to predicted VERY HIGH CPU usage.")
            continue

    # Start the scheduler
    scheduler.start()
    print("Scheduler started.")

