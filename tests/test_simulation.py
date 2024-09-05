import pytest
from simulation_model.wl_simulation import run_simulations, Service, Patient

def test_patient_initialization():
    patient = Patient(patient_id=1, waiting_time=0)
    assert patient.patient_id == 1
    assert patient.waiting_time == 0
    assert not patient.completed_treatment

def test_service_initialization():
    service = Service(dna_rate=0.1, proportion_dna_discharged=0.2, cancellation_rate=0.05)
    assert service.dna_rate == 0.1
    assert service.proportion_dna_discharged == 0.2
    assert service.cancellation_rate == 0.05
    assert service.waiting_list == []

def test_add_to_waiting_list():
    service = Service()
    patient = Patient(patient_id=1)
    service.add_to_waiting_list(patient)
    assert len(service.waiting_list) == 1
    assert service.waiting_list[0] == patient

def test_select_patients_for_treatment():
    service = Service()
    patients = [Patient(patient_id=i, waiting_time=i) for i in range(10)]
    service.waiting_list = patients
    selected_patients = service.select_patients_for_treatment(patients, capacity=5)
    assert len(selected_patients) == 5
    assert selected_patients[0].patient_id == 5  # Should be the 6th patient (max waiting time)
    assert selected_patients[-1].patient_id == 9  # Should be the last patient (max waiting time)

def test_run_simulations():
    results = run_simulations(num_simulations=1, time_steps=1, capacity=[1], mean_arr=1)
    assert not results.empty
    assert 'patient_id' in results.columns
    assert 'waiting_time' in results.columns
    assert 'timestamp' in results.columns
    assert 'sim_num' in results.columns