"""
Appointment Scheduling and Queue Management Backend Service

This module provides core functionality for managing patient appointments
in an Electronic Medical Records (EMR) system.
"""

from datetime import datetime, date, time
from typing import List, Dict, Optional, Union
import uuid
import json
import copy


# Data Models
class AppointmentStatus:
    CONFIRMED = "Confirmed"
    SCHEDULED = "Scheduled"
    UPCOMING = "Upcoming"
    CANCELLED = "Cancelled"


class AppointmentMode:
    ONLINE = "online"
    IN_PERSON = "in-person"


# Mock Data Store - 10+ sample appointments
# Idempotency key tracking for duplicate operation prevention
idempotency_keys = {}

appointments_db = [
    {
        "id": "apt_001",
        "patientName": "John Smith",
        "date": "2024-01-15",
        "time": "09:00",
        "duration": 30,
        "doctorName": "Dr. Johnson",
        "status": AppointmentStatus.CONFIRMED,
        "mode": AppointmentMode.IN_PERSON
    },
    {
        "id": "apt_002",
        "patientName": "Sarah Wilson",
        "date": "2024-01-15",
        "time": "10:30",
        "duration": 45,
        "doctorName": "Dr. Smith",
        "status": AppointmentStatus.SCHEDULED,
        "mode": AppointmentMode.ONLINE
    },
    {
        "id": "apt_003",
        "patientName": "Michael Brown",
        "date": "2024-01-16",
        "time": "14:00",
        "duration": 60,
        "doctorName": "Dr. Johnson",
        "status": AppointmentStatus.UPCOMING,
        "mode": AppointmentMode.IN_PERSON
    },
    {
        "id": "apt_004",
        "patientName": "Emily Davis",
        "date": "2024-01-16",
        "time": "11:15",
        "duration": 30,
        "doctorName": "Dr. Williams",
        "status": AppointmentStatus.CONFIRMED,
        "mode": AppointmentMode.ONLINE
    },
    {
        "id": "apt_005",
        "patientName": "Robert Taylor",
        "date": "2024-01-17",
        "time": "08:30",
        "duration": 45,
        "doctorName": "Dr. Smith",
        "status": AppointmentStatus.SCHEDULED,
        "mode": AppointmentMode.IN_PERSON
    },
    {
        "id": "apt_006",
        "patientName": "Lisa Anderson",
        "date": "2024-01-17",
        "time": "13:45",
        "duration": 30,
        "doctorName": "Dr. Johnson",
        "status": AppointmentStatus.CANCELLED,
        "mode": AppointmentMode.ONLINE
    },
    {
        "id": "apt_007",
        "patientName": "David Martinez",
        "date": "2024-01-18",
        "time": "10:00",
        "duration": 60,
        "doctorName": "Dr. Williams",
        "status": AppointmentStatus.UPCOMING,
        "mode": AppointmentMode.IN_PERSON
    },
    {
        "id": "apt_008",
        "patientName": "Jennifer Garcia",
        "date": "2024-01-18",
        "time": "15:30",
        "duration": 45,
        "doctorName": "Dr. Smith",
        "status": AppointmentStatus.CONFIRMED,
        "mode": AppointmentMode.ONLINE
    },
    {
        "id": "apt_009",
        "patientName": "Christopher Lee",
        "date": "2024-01-19",
        "time": "09:15",
        "duration": 30,
        "doctorName": "Dr. Johnson",
        "status": AppointmentStatus.SCHEDULED,
        "mode": AppointmentMode.IN_PERSON
    },
    {
        "id": "apt_010",
        "patientName": "Amanda White",
        "date": "2024-01-19",
        "time": "16:00",
        "duration": 45,
        "doctorName": "Dr. Williams",
        "status": AppointmentStatus.UPCOMING,
        "mode": AppointmentMode.ONLINE
    },
    {
        "id": "apt_011",
        "patientName": "Kevin Thompson",
        "date": "2024-01-20",
        "time": "11:30",
        "duration": 60,
        "doctorName": "Dr. Smith",
        "status": AppointmentStatus.CONFIRMED,
        "mode": AppointmentMode.IN_PERSON
    },
    {
        "id": "apt_012",
        "patientName": "Michelle Rodriguez",
        "date": "2024-01-20",
        "time": "14:15",
        "duration": 30,
        "doctorName": "Dr. Johnson",
        "status": AppointmentStatus.SCHEDULED,
        "mode": AppointmentMode.ONLINE
    }
]


# Core CRUD Operation Function Signatures

def get_appointments(filters: Optional[Dict[str, str]] = None) -> List[Dict]:
    """
    Retrieve appointments with optional filtering.
    
    Args:
        filters: Optional dictionary with keys: date, status, doctorName
        
    Returns:
        List of appointment dictionaries matching the filter criteria
    """
    if filters is None:
        filters = {}
    
    # Input validation
    if not isinstance(filters, dict):
        raise ValueError("Filters must be a dictionary")
    
    # Validate filter keys
    valid_filter_keys = {'date', 'status', 'doctorName'}
    invalid_keys = set(filters.keys()) - valid_filter_keys
    if invalid_keys:
        raise ValueError(f"Invalid filter keys: {invalid_keys}. Valid keys are: {valid_filter_keys}")
    
    # Validate status filter if provided
    if 'status' in filters and filters['status'] and not is_valid_status(filters['status']):
        raise ValueError(f"Invalid status: {filters['status']}")
    
    # Start with all appointments
    result = appointments_db.copy()
    
    # Apply date filter
    if 'date' in filters and filters['date']:
        try:
            # Validate date format
            datetime.strptime(filters['date'], '%Y-%m-%d')
            result = [apt for apt in result if apt['date'] == filters['date']]
        except ValueError:
            raise ValueError(f"Invalid date format: {filters['date']}. Expected YYYY-MM-DD")
    
    # Apply status filter
    if 'status' in filters and filters['status']:
        result = [apt for apt in result if apt['status'] == filters['status']]
    
    # Apply doctor name filter
    if 'doctorName' in filters and filters['doctorName']:
        result = [apt for apt in result if apt['doctorName'] == filters['doctorName']]
    
    # Return deep copies to ensure idempotency
    return [copy.deepcopy(apt) for apt in result]


def get_appointment_by_id(appointment_id: str) -> Optional[Dict]:
    """
    Retrieve a single appointment by its ID.
    
    Args:
        appointment_id: Unique identifier for the appointment
        
    Returns:
        Appointment dictionary if found, None otherwise
    """
    if not appointment_id:
        raise ValueError("Appointment ID cannot be empty")
    
    if not isinstance(appointment_id, str):
        raise ValueError("Appointment ID must be a string")
    
    for appointment in appointments_db:
        if appointment['id'] == appointment_id:
            return copy.deepcopy(appointment)
    
    return None


def create_appointment(payload: Dict, idempotency_key: Optional[str] = None) -> Dict:
    """
    Create a new appointment with validation and conflict detection.
    
    Args:
        payload: Dictionary containing appointment data
        idempotency_key: Optional key to prevent duplicate operations
        
    Returns:
        Created appointment dictionary with generated ID and default status
        
    Raises:
        ValueError: If payload validation fails or scheduling conflicts exist
    """
    # Handle idempotency key for duplicate operation prevention
    if idempotency_key:
        if idempotency_key in idempotency_keys:
            # Return the previously created appointment for this key
            return copy.deepcopy(idempotency_keys[idempotency_key])
    
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    
    # Use detailed validation for comprehensive error messages
    is_valid, validation_errors = validate_appointment_data_detailed(payload)
    if not is_valid:
        raise ValueError(f"Validation failed: {'; '.join(validation_errors)}")
    
    # Create new appointment with generated unique ID and default status
    new_appointment = {
        'id': generate_unique_id_with_retry(),  # Use retry mechanism for uniqueness
        'patientName': payload['patientName'],
        'date': payload['date'],
        'time': payload['time'],
        'duration': payload['duration'],
        'doctorName': payload['doctorName'],
        'status': AppointmentStatus.SCHEDULED,  # Default status
        'mode': payload['mode']
    }
    
    # Detect scheduling conflicts
    conflicts = detect_scheduling_conflicts(new_appointment)
    if conflicts:
        conflict_details = [f"Conflict with appointment {c['id']} at {c['time']}" for c in conflicts]
        raise ValueError(f"Scheduling conflicts detected: {'; '.join(conflict_details)}")
    
    # Add to database
    appointments_db.append(new_appointment)
    
    # Store idempotency key if provided
    if idempotency_key:
        idempotency_keys[idempotency_key] = copy.deepcopy(new_appointment)
    
    return copy.deepcopy(new_appointment)


def update_appointment_status(appointment_id: str, new_status: str, idempotency_key: Optional[str] = None) -> Dict:
    """
    Update the status of an existing appointment.
    
    Args:
        appointment_id: Unique identifier for the appointment
        new_status: New status value (must be valid AppointmentStatus)
        idempotency_key: Optional key to prevent duplicate operations
        
    Returns:
        Updated appointment dictionary
        
    Raises:
        ValueError: If appointment not found or invalid status
    """
    # Handle idempotency key for duplicate operation prevention
    if idempotency_key:
        if idempotency_key in idempotency_keys:
            # Return the previously updated appointment for this key
            return copy.deepcopy(idempotency_keys[idempotency_key])
    
    if not appointment_id:
        raise ValueError("Appointment ID cannot be empty")
    
    if not isinstance(appointment_id, str):
        raise ValueError("Appointment ID must be a string")
    
    if not is_valid_status(new_status):
        raise ValueError(f"Invalid status: {new_status}")
    
    # Find the appointment
    for appointment in appointments_db:
        if appointment['id'] == appointment_id:
            appointment['status'] = new_status
            updated_appointment = copy.deepcopy(appointment)
            
            # Store idempotency key if provided
            if idempotency_key:
                idempotency_keys[idempotency_key] = updated_appointment
            
            return updated_appointment
    
    raise ValueError(f"Appointment not found: {appointment_id}")


def delete_appointment(appointment_id: str) -> bool:
    """
    Delete an appointment from the system.
    
    Args:
        appointment_id: Unique identifier for the appointment
        
    Returns:
        True if deletion successful, False if appointment not found
    """
    if not appointment_id:
        raise ValueError("Appointment ID cannot be empty")
    
    if not isinstance(appointment_id, str):
        raise ValueError("Appointment ID must be a string")
    
    # Find and remove the appointment
    for i, appointment in enumerate(appointments_db):
        if appointment['id'] == appointment_id:
            appointments_db.pop(i)
            return True
    
    return False


# Utility Functions

def validate_appointment_data(data: Dict) -> bool:
    """
    Validate appointment data structure and required fields.
    
    Args:
        data: Appointment data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Validate patient name
        if not isinstance(data.get('patientName'), str) or not data['patientName'].strip():
            return False
        
        # Validate date format
        datetime.strptime(data['date'], '%Y-%m-%d')
        
        # Validate time format
        datetime.strptime(data['time'], '%H:%M')
        
        # Validate duration
        if not isinstance(data.get('duration'), int) or data['duration'] <= 0:
            return False
        
        # Validate doctor name
        if not isinstance(data.get('doctorName'), str) or not data['doctorName'].strip():
            return False
        
        # Validate mode
        if not is_valid_mode(data.get('mode')):
            return False
        
        return True
    except (ValueError, KeyError, TypeError):
        return False


def validate_appointment_data_detailed(data: Dict) -> tuple[bool, List[str]]:
    """
    Validate appointment data structure and required fields with detailed error messages.
    
    Args:
        data: Appointment data dictionary
        
    Returns:
        Tuple of (is_valid: bool, error_messages: List[str])
    """
    errors = []
    
    if not isinstance(data, dict):
        return False, ["Appointment data must be a dictionary"]
    
    # Validate patient name
    if 'patientName' not in data:
        errors.append("Patient name is required")
    elif not isinstance(data['patientName'], str):
        errors.append("Patient name must be a string")
    elif not data['patientName'].strip():
        errors.append("Patient name cannot be empty or whitespace only")
    
    # Validate date format
    if 'date' not in data:
        errors.append("Date is required")
    elif not isinstance(data['date'], str):
        errors.append("Date must be a string")
    else:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            errors.append("Date must be in YYYY-MM-DD format")
    
    # Validate time format
    if 'time' not in data:
        errors.append("Time is required")
    elif not isinstance(data['time'], str):
        errors.append("Time must be a string")
    else:
        try:
            datetime.strptime(data['time'], '%H:%M')
        except ValueError:
            errors.append("Time must be in HH:MM format (24-hour)")
    
    # Validate duration
    if 'duration' not in data:
        errors.append("Duration is required")
    elif not isinstance(data['duration'], int):
        errors.append("Duration must be an integer")
    elif data['duration'] <= 0:
        errors.append("Duration must be greater than 0 minutes")
    elif data['duration'] > 480:  # 8 hours max
        errors.append("Duration cannot exceed 480 minutes (8 hours)")
    
    # Validate doctor name
    if 'doctorName' not in data:
        errors.append("Doctor name is required")
    elif not isinstance(data['doctorName'], str):
        errors.append("Doctor name must be a string")
    elif not data['doctorName'].strip():
        errors.append("Doctor name cannot be empty or whitespace only")
    
    # Validate mode
    if 'mode' not in data:
        errors.append("Appointment mode is required")
    elif not isinstance(data['mode'], str):
        errors.append("Appointment mode must be a string")
    elif not is_valid_mode(data['mode']):
        valid_modes = [AppointmentMode.ONLINE, AppointmentMode.IN_PERSON]
        errors.append(f"Appointment mode must be one of: {', '.join(valid_modes)}")
    
    return len(errors) == 0, errors


def ensure_unique_appointment_id(appointment_id: str) -> bool:
    """
    Ensure the given appointment ID is unique in the database.
    
    Args:
        appointment_id: The ID to check for uniqueness
        
    Returns:
        True if unique, False if already exists
    """
    return not any(apt['id'] == appointment_id for apt in appointments_db)


def generate_unique_id_with_retry(max_retries: int = 10) -> str:
    """
    Generate a unique appointment ID with retry mechanism.
    
    Args:
        max_retries: Maximum number of attempts to generate a unique ID
        
    Returns:
        Unique string identifier
        
    Raises:
        RuntimeError: If unable to generate unique ID after max_retries
    """
    for _ in range(max_retries):
        new_id = f"apt_{str(uuid.uuid4())[:8]}"
        if ensure_unique_appointment_id(new_id):
            return new_id
    
    raise RuntimeError(f"Unable to generate unique appointment ID after {max_retries} attempts")


def detect_scheduling_conflicts(appointment: Dict) -> List[Dict]:
    """
    Detect scheduling conflicts for a given appointment.
    
    Args:
        appointment: Appointment data to check for conflicts
        
    Returns:
        List of conflicting appointments
    """
    conflicts = []
    
    # Parse appointment time details
    try:
        apt_date = appointment['date']
        apt_time = datetime.strptime(appointment['time'], '%H:%M').time()
        apt_duration = appointment['duration']
        apt_doctor = appointment['doctorName']
        
        # Calculate end time
        apt_start_minutes = apt_time.hour * 60 + apt_time.minute
        apt_end_minutes = apt_start_minutes + apt_duration
        
        # Check against existing appointments
        for existing_apt in appointments_db:
            # Skip if different date or doctor
            if existing_apt['date'] != apt_date or existing_apt['doctorName'] != apt_doctor:
                continue
            
            # Skip if same appointment (for updates)
            if existing_apt.get('id') == appointment.get('id'):
                continue
            
            # Parse existing appointment time
            existing_time = datetime.strptime(existing_apt['time'], '%H:%M').time()
            existing_start_minutes = existing_time.hour * 60 + existing_time.minute
            existing_end_minutes = existing_start_minutes + existing_apt['duration']
            
            # Check for overlap
            if (apt_start_minutes < existing_end_minutes and apt_end_minutes > existing_start_minutes):
                conflicts.append(existing_apt.copy())
    
    except (ValueError, KeyError):
        # If we can't parse the appointment data, return empty conflicts
        pass
    
    return conflicts


def generate_unique_id() -> str:
    """
    Generate a unique appointment ID.
    
    Returns:
        Unique string identifier
    """
    return generate_unique_id_with_retry()


def is_valid_status(status: str) -> bool:
    """
    Check if a status value is valid.
    
    Args:
        status: Status string to validate
        
    Returns:
        True if valid status, False otherwise
    """
    valid_statuses = [
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.UPCOMING,
        AppointmentStatus.CANCELLED
    ]
    return status in valid_statuses


def is_valid_mode(mode: str) -> bool:
    """
    Check if a mode value is valid.
    
    Args:
        mode: Mode string to validate
        
    Returns:
        True if valid mode, False otherwise
    """
    valid_modes = [AppointmentMode.ONLINE, AppointmentMode.IN_PERSON]
    return mode in valid_modes


def clear_idempotency_keys() -> None:
    """
    Clear all stored idempotency keys.
    
    This function is primarily for testing and maintenance purposes.
    """
    global idempotency_keys
    idempotency_keys.clear()


def get_idempotency_key_count() -> int:
    """
    Get the number of stored idempotency keys.
    
    Returns:
        Number of stored idempotency keys
    """
    return len(idempotency_keys)


# Edge Case Handling Functions

def get_overlapping_appointments(appointments: List[Dict], date: str = None) -> Dict[str, List[Dict]]:
    """
    Identify and group overlapping appointments by time slot and doctor.
    
    Args:
        appointments: List of appointment dictionaries
        date: Optional date filter (YYYY-MM-DD format)
        
    Returns:
        Dictionary mapping time slots to lists of overlapping appointments
    """
    if not appointments:
        return {}
    
    # Filter by date if provided
    if date:
        appointments = [apt for apt in appointments if apt.get('date') == date]
    
    overlaps = {}
    
    for i, apt1 in enumerate(appointments):
        for j, apt2 in enumerate(appointments[i + 1:], i + 1):
            # Skip if different dates or doctors
            if (apt1.get('date') != apt2.get('date') or 
                apt1.get('doctorName') != apt2.get('doctorName')):
                continue
            
            # Check for time overlap
            try:
                apt1_start = datetime.strptime(apt1.get('time', ''), '%H:%M').time()
                apt1_duration = apt1.get('duration', 0)
                apt1_start_minutes = apt1_start.hour * 60 + apt1_start.minute
                apt1_end_minutes = apt1_start_minutes + apt1_duration
                
                apt2_start = datetime.strptime(apt2.get('time', ''), '%H:%M').time()
                apt2_duration = apt2.get('duration', 0)
                apt2_start_minutes = apt2_start.hour * 60 + apt2_start.minute
                apt2_end_minutes = apt2_start_minutes + apt2_duration
                
                # Check for overlap
                if (apt1_start_minutes < apt2_end_minutes and apt2_start_minutes < apt1_end_minutes):
                    # Create overlap key
                    overlap_key = f"{apt1.get('date')}_{apt1.get('doctorName')}_{min(apt1_start_minutes, apt2_start_minutes)}"
                    
                    if overlap_key not in overlaps:
                        overlaps[overlap_key] = []
                    
                    # Add both appointments if not already present
                    apt1_ids = [apt.get('id') for apt in overlaps[overlap_key]]
                    if apt1.get('id') not in apt1_ids:
                        overlaps[overlap_key].append(copy.deepcopy(apt1))
                    if apt2.get('id') not in apt1_ids:
                        overlaps[overlap_key].append(copy.deepcopy(apt2))
                        
            except (ValueError, TypeError):
                # Skip appointments with invalid time data
                continue
    
    return overlaps


def handle_empty_appointment_scenarios() -> Dict[str, str]:
    """
    Provide appropriate messages and handling for empty appointment scenarios.
    
    Returns:
        Dictionary with empty state messages and suggestions
    """
    return {
        'no_appointments': 'No appointments found for the selected criteria.',
        'no_appointments_today': 'No appointments scheduled for today.',
        'no_upcoming_appointments': 'No upcoming appointments found.',
        'no_past_appointments': 'No past appointments found.',
        'no_appointments_for_doctor': 'No appointments found for the selected doctor.',
        'suggestions': [
            'Try adjusting your date range',
            'Check if appointments exist for other doctors',
            'Create a new appointment using the "New Appointment" button',
            'Clear any active filters to see all appointments'
        ]
    }


def validate_date_range(start_date: str, end_date: str) -> tuple[bool, str]:
    """
    Validate date range inputs for appointment queries.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start > end:
            return False, "Start date cannot be after end date"
        
        # Check for reasonable date range (not more than 1 year)
        if (end - start).days > 365:
            return False, "Date range cannot exceed 365 days"
        
        return True, ""
        
    except ValueError as e:
        return False, f"Invalid date format: {str(e)}"


def get_appointments_with_overlap_detection(filters: Optional[Dict[str, str]] = None) -> Dict:
    """
    Get appointments with additional overlap detection and empty state handling.
    
    Args:
        filters: Optional dictionary with keys: date, status, doctorName, start_date, end_date
        
    Returns:
        Dictionary containing appointments, overlaps, and metadata
    """
    if filters is None:
        filters = {}
    
    # Validate date range if provided
    if 'start_date' in filters and 'end_date' in filters:
        is_valid, error_msg = validate_date_range(filters['start_date'], filters['end_date'])
        if not is_valid:
            raise ValueError(error_msg)
    
    # Get appointments using existing function
    appointments = get_appointments(filters)
    
    # Detect overlaps
    overlaps = get_overlapping_appointments(appointments, filters.get('date'))
    
    # Get empty state messages if needed
    empty_state = handle_empty_appointment_scenarios()
    
    # Calculate metadata
    metadata = {
        'total_count': len(appointments),
        'has_overlaps': len(overlaps) > 0,
        'overlap_count': len(overlaps),
        'unique_dates': len(set(apt.get('date', '') for apt in appointments)),
        'unique_doctors': len(set(apt.get('doctorName', '') for apt in appointments)),
        'applied_filters': filters
    }
    
    return {
        'appointments': appointments,
        'overlaps': overlaps,
        'empty_state': empty_state,
        'metadata': metadata
    }


def get_appointments_by_time_slot(date: str, doctor_name: Optional[str] = None) -> Dict[str, List[Dict]]:
    """
    Get appointments organized by time slots for better calendar display.
    
    Args:
        date: Date in YYYY-MM-DD format
        doctor_name: Optional doctor name filter
        
    Returns:
        Dictionary mapping time slots to lists of appointments
    """
    filters = {'date': date}
    if doctor_name:
        filters['doctorName'] = doctor_name
    
    appointments = get_appointments(filters)
    
    # Group appointments by time slot
    time_slots = {}
    
    for appointment in appointments:
        time_slot = appointment.get('time', '00:00')
        if time_slot not in time_slots:
            time_slots[time_slot] = []
        time_slots[time_slot].append(appointment)
    
    # Sort appointments within each time slot by duration (longer first for better display)
    for time_slot in time_slots:
        time_slots[time_slot].sort(key=lambda apt: apt.get('duration', 0), reverse=True)
    
    return time_slots


def get_appointment_conflicts_summary(date: str = None) -> Dict:
    """
    Get a summary of appointment conflicts for administrative review.
    
    Args:
        date: Optional date filter (YYYY-MM-DD format)
        
    Returns:
        Dictionary containing conflict summary and recommendations
    """
    filters = {}
    if date:
        filters['date'] = date
    
    appointments = get_appointments(filters)
    overlaps = get_overlapping_appointments(appointments, date)
    
    # Analyze conflicts
    conflict_summary = {
        'total_conflicts': len(overlaps),
        'affected_appointments': 0,
        'doctors_with_conflicts': set(),
        'dates_with_conflicts': set(),
        'conflict_details': [],
        'recommendations': []
    }
    
    for overlap_key, conflicting_appointments in overlaps.items():
        conflict_summary['affected_appointments'] += len(conflicting_appointments)
        
        # Track doctors and dates with conflicts
        for apt in conflicting_appointments:
            conflict_summary['doctors_with_conflicts'].add(apt.get('doctorName', ''))
            conflict_summary['dates_with_conflicts'].add(apt.get('date', ''))
        
        # Create conflict detail
        conflict_detail = {
            'conflict_id': overlap_key,
            'appointment_count': len(conflicting_appointments),
            'doctor': conflicting_appointments[0].get('doctorName', ''),
            'date': conflicting_appointments[0].get('date', ''),
            'time_range': f"{min(apt.get('time', '') for apt in conflicting_appointments)} - {max(apt.get('time', '') for apt in conflicting_appointments)}",
            'appointments': [
                {
                    'id': apt.get('id', ''),
                    'patient': apt.get('patientName', ''),
                    'time': apt.get('time', ''),
                    'duration': apt.get('duration', 0),
                    'status': apt.get('status', '')
                }
                for apt in conflicting_appointments
            ]
        }
        conflict_summary['conflict_details'].append(conflict_detail)
    
    # Convert sets to lists for JSON serialization
    conflict_summary['doctors_with_conflicts'] = list(conflict_summary['doctors_with_conflicts'])
    conflict_summary['dates_with_conflicts'] = list(conflict_summary['dates_with_conflicts'])
    
    # Generate recommendations
    if conflict_summary['total_conflicts'] > 0:
        conflict_summary['recommendations'] = [
            f"Review {conflict_summary['total_conflicts']} scheduling conflicts",
            f"Contact {len(conflict_summary['doctors_with_conflicts'])} doctor(s) to resolve overlaps",
            "Consider rescheduling conflicting appointments",
            "Implement appointment buffer times to prevent future conflicts",
            "Review scheduling policies for same-doctor appointments"
        ]
    else:
        conflict_summary['recommendations'] = [
            "No scheduling conflicts detected",
            "Current appointment schedule is optimally organized",
            "Continue monitoring for future conflicts"
        ]
    
    return conflict_summary


def handle_multiple_appointments_per_slot(appointments: List[Dict], max_per_slot: int = 3) -> Dict:
    """
    Handle scenarios where multiple appointments exist in the same time slot.
    
    Args:
        appointments: List of appointment dictionaries
        max_per_slot: Maximum recommended appointments per time slot
        
    Returns:
        Dictionary with organized appointments and warnings
    """
    # Group by date, doctor, and time
    slot_groups = {}
    
    for appointment in appointments:
        date = appointment.get('date', '')
        doctor = appointment.get('doctorName', '')
        time = appointment.get('time', '')
        
        slot_key = f"{date}_{doctor}_{time}"
        
        if slot_key not in slot_groups:
            slot_groups[slot_key] = []
        slot_groups[slot_key].append(appointment)
    
    # Analyze slot occupancy
    result = {
        'organized_slots': {},
        'overbooked_slots': {},
        'warnings': [],
        'statistics': {
            'total_slots': len(slot_groups),
            'overbooked_count': 0,
            'max_appointments_in_slot': 0,
            'average_appointments_per_slot': 0
        }
    }
    
    total_appointments = 0
    
    for slot_key, slot_appointments in slot_groups.items():
        appointment_count = len(slot_appointments)
        total_appointments += appointment_count
        
        # Update statistics
        if appointment_count > result['statistics']['max_appointments_in_slot']:
            result['statistics']['max_appointments_in_slot'] = appointment_count
        
        if appointment_count > max_per_slot:
            result['overbooked_slots'][slot_key] = slot_appointments
            result['statistics']['overbooked_count'] += 1
            
            # Generate warning
            sample_apt = slot_appointments[0]
            warning = {
                'type': 'overbooked_slot',
                'message': f"Time slot {sample_apt.get('time', '')} on {sample_apt.get('date', '')} for {sample_apt.get('doctorName', '')} has {appointment_count} appointments (max recommended: {max_per_slot})",
                'slot_key': slot_key,
                'appointment_count': appointment_count,
                'appointments': [apt.get('id', '') for apt in slot_appointments]
            }
            result['warnings'].append(warning)
        else:
            result['organized_slots'][slot_key] = slot_appointments
    
    # Calculate average
    if len(slot_groups) > 0:
        result['statistics']['average_appointments_per_slot'] = round(total_appointments / len(slot_groups), 2)
    
    return result


# Enhanced Error Handling and Network Simulation Functions

class NetworkError(Exception):
    """Custom exception for simulating network errors."""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors with detailed messages."""
    def __init__(self, message: str, field_errors: Dict[str, str] = None):
        super().__init__(message)
        self.field_errors = field_errors or {}

class ConcurrencyError(Exception):
    """Custom exception for concurrent operation conflicts."""
    pass

def simulate_network_failure(failure_rate: float = 0.1) -> None:
    """
    Simulate network failures for testing error handling.
    
    Args:
        failure_rate: Probability of failure (0.0 to 1.0)
    
    Raises:
        NetworkError: Randomly based on failure_rate
    """
    import random
    if random.random() < failure_rate:
        error_types = [
            "Connection timeout",
            "Network unreachable", 
            "Service temporarily unavailable",
            "DNS resolution failed",
            "Connection refused"
        ]
        raise NetworkError(f"Network error: {random.choice(error_types)}")

def validate_concurrent_operation(operation_id: str, resource_id: str) -> None:
    """
    Simulate concurrent operation validation.
    
    Args:
        operation_id: Unique identifier for the operation
        resource_id: ID of the resource being modified
        
    Raises:
        ConcurrencyError: If concurrent modification detected
    """
    # In a real system, this would check for concurrent modifications
    # For simulation, we'll randomly trigger conflicts
    import random
    if random.random() < 0.05:  # 5% chance of concurrency conflict
        raise ConcurrencyError(f"Resource {resource_id} is being modified by another operation")

def handle_api_error(func):
    """
    Decorator to add consistent error handling to API functions.
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Wrapped function with enhanced error handling
    """
    def wrapper(*args, **kwargs):
        try:
            # Simulate network issues in testing
            if kwargs.get('_simulate_network_failure', False):
                simulate_network_failure(kwargs.get('_failure_rate', 0.1))
            
            # Simulate concurrency checks
            if kwargs.get('_check_concurrency', False):
                operation_id = kwargs.get('_operation_id', 'default')
                resource_id = kwargs.get('_resource_id', 'default')
                validate_concurrent_operation(operation_id, resource_id)
            
            return func(*args, **kwargs)
            
        except NetworkError as e:
            # Re-raise network errors for client handling
            raise e
        except ConcurrencyError as e:
            # Re-raise concurrency errors for client handling  
            raise e
        except ValidationError as e:
            # Re-raise validation errors with field details
            raise e
        except ValueError as e:
            # Convert ValueError to ValidationError for consistency
            raise ValidationError(str(e))
        except Exception as e:
            # Wrap unexpected errors
            raise RuntimeError(f"Unexpected error in {func.__name__}: {str(e)}")
    
    return wrapper

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Retry function with exponential backoff for network errors.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        
    Returns:
        Function result or raises last exception
    """
    import time
    import random
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except NetworkError as e:
            last_exception = e
            if attempt < max_retries:
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue
            else:
                raise e
        except Exception as e:
            # Don't retry non-network errors
            raise e
    
    # This should never be reached, but just in case
    raise last_exception

def graceful_degradation_wrapper(func, fallback_value=None):
    """
    Wrapper to provide graceful degradation for non-critical operations.
    
    Args:
        func: Function to wrap
        fallback_value: Value to return if function fails
        
    Returns:
        Function result or fallback value
    """
    try:
        return func()
    except Exception as e:
        # Log error in production
        print(f"Warning: {func.__name__} failed with {str(e)}, using fallback")
        return fallback_value

# Dashboard Metrics Functions

def get_dashboard_metrics() -> Dict:
    """
    Calculate and return dashboard metrics for appointment statistics.
    
    Returns:
        Dictionary containing appointment statistics and summaries
    """
    if not appointments_db:
        return {
            'totalAppointments': 0,
            'statusCounts': {
                'Confirmed': 0,
                'Scheduled': 0,
                'Upcoming': 0,
                'Cancelled': 0
            },
            'modeCounts': {
                'online': 0,
                'in-person': 0
            },
            'doctorCounts': {},
            'recentActivity': [],
            'schedulingPatterns': {
                'averageDuration': 0,
                'mostCommonDuration': 0,
                'peakHours': [],
                'busyDays': []
            }
        }
    
    # Calculate basic counts
    total_appointments = len(appointments_db)
    
    # Status counts
    status_counts = {
        'Confirmed': 0,
        'Scheduled': 0,
        'Upcoming': 0,
        'Cancelled': 0
    }
    
    # Mode counts
    mode_counts = {
        'online': 0,
        'in-person': 0
    }
    
    # Doctor counts
    doctor_counts = {}
    
    # Duration tracking for patterns
    durations = []
    hours = []
    dates = []
    
    # Process each appointment
    for appointment in appointments_db:
        # Count by status
        status = appointment.get('status', 'Unknown')
        if status in status_counts:
            status_counts[status] += 1
        
        # Count by mode
        mode = appointment.get('mode', 'unknown')
        if mode in mode_counts:
            mode_counts[mode] += 1
        
        # Count by doctor
        doctor = appointment.get('doctorName', 'Unknown')
        doctor_counts[doctor] = doctor_counts.get(doctor, 0) + 1
        
        # Collect data for patterns
        durations.append(appointment.get('duration', 0))
        
        # Extract hour from time for peak hour analysis
        try:
            time_str = appointment.get('time', '00:00')
            hour = int(time_str.split(':')[0])
            hours.append(hour)
        except (ValueError, IndexError):
            pass
        
        # Collect dates for busy day analysis
        dates.append(appointment.get('date', ''))
    
    # Calculate scheduling patterns
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Most common duration
    duration_counts = {}
    for duration in durations:
        duration_counts[duration] = duration_counts.get(duration, 0) + 1
    most_common_duration = max(duration_counts.keys(), key=lambda k: duration_counts[k]) if duration_counts else 0
    
    # Peak hours (most common appointment hours)
    hour_counts = {}
    for hour in hours:
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    # Get top 3 peak hours
    peak_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:3]
    
    # Busy days (dates with most appointments)
    date_counts = {}
    for date in dates:
        if date:  # Skip empty dates
            date_counts[date] = date_counts.get(date, 0) + 1
    
    # Get top 5 busy days
    busy_days = sorted(date_counts.keys(), key=lambda d: date_counts[d], reverse=True)[:5]
    
    # Recent activity (last 5 appointments by date/time)
    recent_activity = []
    try:
        # Sort appointments by date and time (most recent first)
        sorted_appointments = sorted(
            appointments_db,
            key=lambda apt: (apt.get('date', ''), apt.get('time', '')),
            reverse=True
        )
        
        for apt in sorted_appointments[:5]:
            recent_activity.append({
                'id': apt.get('id', ''),
                'patientName': apt.get('patientName', ''),
                'date': apt.get('date', ''),
                'time': apt.get('time', ''),
                'doctorName': apt.get('doctorName', ''),
                'status': apt.get('status', ''),
                'action': 'scheduled'  # In a real system, this would track actual actions
            })
    except Exception:
        # If sorting fails, just take first 5
        for apt in appointments_db[:5]:
            recent_activity.append({
                'id': apt.get('id', ''),
                'patientName': apt.get('patientName', ''),
                'date': apt.get('date', ''),
                'time': apt.get('time', ''),
                'doctorName': apt.get('doctorName', ''),
                'status': apt.get('status', ''),
                'action': 'scheduled'
            })
    
    return {
        'totalAppointments': total_appointments,
        'statusCounts': status_counts,
        'modeCounts': mode_counts,
        'doctorCounts': doctor_counts,
        'recentActivity': recent_activity,
        'schedulingPatterns': {
            'averageDuration': round(avg_duration, 1),
            'mostCommonDuration': most_common_duration,
            'peakHours': peak_hours,
            'busyDays': busy_days
        }
    }