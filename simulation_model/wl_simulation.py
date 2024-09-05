## Queueing Model
 
import pandas as pd
import numpy as np
import random
import copy

 
class Patient:
 
    """
    Stores information on each patient entering the waiting list.
    """
 
    def __init__(self, patient_id, waiting_time=0):
 
 
        """
        Args:
            - patient_id (int): Unique integer for each patient entering the system.
            - waiting_time (int): Number of time periods spent in system.
        """
 
        self.patient_id = patient_id
        self.waiting_time = waiting_time
        self.completed_treatment = False
        
        
class Service:
 
 
    """
    Deals with patients being treated by the service.
    """
 
    def __init__(self, 
                 initial_queue=None, 
                 dna_rate = 0.05, 
                 proportion_dna_discharged = 0.05, 
                 cancellation_rate = 0.01):
 
        """
        Args:
            - initial_queue (list): List of patients (of type from class Patient)
            - dna_rate (float): Percentage of DNAs each time step.
            - proportion_dna_discharged (float): Of the patients that DNA, percentage that are subsequently discharged.
            - cancellation_rate (float): Percentage of cancellations each week (from entire waiting list).
        """
 
        # Store patients in system.
        if initial_queue is not None:
            self.waiting_list = copy.deepcopy(initial_queue)
        else:
            self.waiting_list = []
 
        self.dna_rate = dna_rate
        self.proportion_dna_discharged = proportion_dna_discharged
        self.cancellation_rate = cancellation_rate
        self.patient_counter = len(self.waiting_list)  # Counter for unique patient IDs
 
 
    def add_to_waiting_list(self, patient):
 
        """
        Adds patients to waiting_list.
        
        Args:
            - patient (object from Patient class). Appended to waiting list.
        """
 
        self.waiting_list.append(patient)
       
 
    def select_patients_for_treatment(self, patients_waiting, capacity):
 
        '''
        Selecting patients to treat in current time step. Ordered by patient waiting time.
       
        Args:
            - patients_waiting (list): Waiting list.
            - capacity (list): Capacity (available appointments) for service.
        '''
       
        selected_patients = []
        sorted_patients = sorted(patients_waiting, key=lambda p: p.waiting_time)
        
        # Select patients for treatment
        selected_patients.extend(sorted_patients[-capacity:])
 
        return selected_patients
 
 
 
    def patient_dna(self, selected_patients):
       
        """
        Patient does not attend appointment but re-enters the waiting list (lost capacity).
        This differs from patient cancellation, as no warning of cancellation is given.
       
        Args:
            - selected_patients (list): Patients selected for treatment (output from select_patients_for_treatment())
        """
       
        # Patient DNAs
        dna_patients = [p for p in selected_patients if random.random() < self.dna_rate]
        
        # Determine patients that DNA and are discharged.
        dna_patients_discharged = [p for p in dna_patients if random.random() < self.proportion_dna_discharged]
        
        # Otherwise, DNA patients rejoin the waiting list.
        dna_patients_rejoin = [p for p in dna_patients if p not in dna_patients_discharged]

        # Patients who were treated (e.g., patients that attended their appointment).
        treated_patients = [p for p in selected_patients if p not in dna_patients_rejoin]

        return treated_patients, dna_patients_discharged
              
                
 
    def update_waiting_time(self):
 
        '''
        Update waiting time for patients not being treated in current time step.
        '''
 
        for patient in self.waiting_list:
            if not patient.completed_treatment:
                patient.waiting_time += 1
 
 
    def treat_patients(self, capacity=None):
 
        """
        Treats patients and flags them as treated.
        Args:
            - capacity (int): Capacity of available slots.
        """
       
 
    
        # Store patient cancellation probabilities as array.
        discharge_proba = np.random.rand(len(self.waiting_list))
        
        # Removing patients with probability less than cancellation rate.
        patients_cancelled = [patient for patient, rand_val in zip(self.waiting_list, discharge_proba) \
                              if rand_val < self.cancellation_rate]
        
        # Flag cancelled patients as discharged.
        for patient in patients_cancelled:
            patient.completed_treatment = True
            
        # Remove cancellations from treatment selection
        patients_waiting = [x for x in self.waiting_list if not x.completed_treatment]
 
        # Select patients for treatment (based on waiting time).
        selected_patients = self.select_patients_for_treatment(patients_waiting, capacity)
 
        # Of patients selected, estimate patient DNA's.
        treated_patients, dna_patients_discharged = self.patient_dna(selected_patients)
 
        # Flag treated patients as completed
        for patient in treated_patients + dna_patients_discharged:
            patient.completed_treatment = True
 
        # Update waiting time for all patients
        self.update_waiting_time()
 
        # Remove treated patients from waiting list
        self.waiting_list = [patient for patient in self.waiting_list if not patient.completed_treatment]
 
 
    def simulate_single_timestep(self, new_patients, capacity, step):
 
        """
        Simulates a single timestep, adding new patients and treating existing ones.
        Args:
            - new_patients (int): Number of new patients joining waiting list at given step.
            - capacity (int): List of available slots for service at given step.
            - step (int): Current time step.
        """ 
 
        self.step = step
 
        for _ in range(new_patients):
            self.patient_counter += 1
            patient_id = self.patient_counter
            patient = Patient(patient_id=patient_id,
                              waiting_time=0)
            self.add_to_waiting_list(patient)

        self.treat_patients(capacity)
 
       
        
        
def run_simulations(num_simulations=50,
                    time_steps=52,
                    initial_queue=None,
                    capacity=None,
                    mean_arr=None,
                    empirical_data=None,
                    linear_growth_rate = 0,
                    dna_rate=0.05,
                    proportion_dna_discharged = 0.05,
                    cancellation_rate = 0.01):
    
    """
    Runs multiple simulations of the queueing simulation.
    
    Args:
        - num_simulations (int): Number of simulations to run.
        - time_steps (int): Number of time steps in each simulation.
        - initial_queue (list): Initial queue of patients.
        - capacity (list): List of slots over forecast horizon.
        - mean_arr (int): Mean arrivals.
        - linear_growth_rate (float): Linear growth rate applied to the patient arrival process.
        - empirical_data (list): Number of additions per time step in the past.
        - dna_rate (float): Percentage of DNAs each time step.
        - proportion_dna_discharged (float): Of the patients that DNA, percentage that are subsequently discharged.
        - cancellation_rate (float): Percentage of cancellations each week (from entire waiting list).

    Returns:
        - pd.DataFrame: Patient level waiting list data (each simulation is concatenated vertically).
    """
    
    wl_simulation_list = []
 
    for sim in range(num_simulations):
        
        # Initialise Service class.
        clinic = Service(initial_queue=initial_queue, 
                         dna_rate=dna_rate,
                         proportion_dna_discharged=proportion_dna_discharged,
                         cancellation_rate=cancellation_rate)
        wl_data = []
 
        for step in range(1, time_steps + 1):

            if empirical_data and priority in empirical_data:
                # Use empirical sampling
                new_patients = random.choice(empirical_data)
            else:
                # Use Poisson distribution with linear growth
                new_patients = np.random.poisson(lam=mean_arr + linear_growth_rate * step)

 
 
            clinic.simulate_single_timestep(new_patients=new_patients,
                                            capacity=capacity[step-1],
                                            step=step)
 
            for p in clinic.waiting_list:
                wl_data.append({
                    'patient_id': p.patient_id,
                    'waiting_time': p.waiting_time,
                    'timestamp': step
                })
                        
 
        wl_df = pd.DataFrame(wl_data)
        wl_df['sim_num'] = sim
        wl_simulation_list.append(wl_df)
        
 
    return pd.concat(wl_simulation_list, ignore_index=True)