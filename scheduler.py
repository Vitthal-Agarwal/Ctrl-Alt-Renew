# scripts/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import time
import random

from simulation import (
    start_high_intensity_computation,
    start_medium_intensity_computation,
    start_low_intensity_computation,
    stop_computation,
)

def schedule_computations(future_df, computation_manager):
    scheduler = BackgroundScheduler()
    
    for idx, row in future_df.iterrows():
        run_time = row['Timestamp'].to_pydatetime()
        predicted_status = row['Predicted_Status']
        
        # Create unique job IDs
        job_id = f'computation_{idx}'
        
        if predicted_status == 0:  # Idle
            scheduler.add_job(
                start_computation,
                'date',
                run_date=run_time,
                id=job_id,
                args=[computation_manager, 'HIGH']
            )
        elif predicted_status == 1:  # Medium Usage
            scheduler.add_job(
                start_computation,
                'date',
                run_date=run_time,
                id=job_id,
                args=[computation_manager, 'MEDIUM']
            )
        elif predicted_status == 2:  # Low Usage
            scheduler.add_job(
                start_computation,
                'date',
                run_date=run_time,
                id=job_id,
                args=[computation_manager, 'LOW']
            )
            
    scheduler.start()
    print("Computation scheduler started.")

def start_computation(computation_manager, intensity):
    # Sample molecules for demonstration
    molecules = [
        "Ethane (C2H6)",
        "Methanol (CH3OH)",
        "Acetaldehyde (C2H4O)",
        "Ethanol (C2H5OH)"
    ]
    
    # Update current calculation
    computation_manager.update_current_calculation(
        cycle=computation_manager.current_calculation['cycle'] + 1,
        molecule=random.choice(molecules)
    )

