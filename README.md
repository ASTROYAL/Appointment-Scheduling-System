# Appointment Scheduling and Queue Management System

A comprehensive Electronic Medical Records (EMR) appointment scheduling system built with Python backend services and React frontend components. This system provides healthcare providers with real-time appointment management, conflict detection, and queue management capabilities.

## Technical Implementation

### GraphQL-Style Query Structure

The `getAppointments` function implements a GraphQL-inspired query structure that allows flexible filtering:

```python
def get_appointments(filters: dict = None) -> List[Dict]:
    """
    GraphQL-style query structure for appointments:
    
    Query Pattern:
    {
      appointments(
        date: "YYYY-MM-DD",
        status: "Confirmed" | "Scheduled" | "Upcoming" | "Cancelled",
        doctorName: "string"
      ) {
        id
        patientName
        date
        time
        duration
        doctorName
        status
        mode
      }
    }
    """
```

**Key Features:**
- **Flexible Filtering**: Supports multiple filter combinations (date, status, doctorName)
- **Type Safety**: Input validation ensures data integrity
- **Consistent Response**: Always returns standardized appointment objects
- **Performance**: Efficient filtering without database overhead (simulated)

### Data Consistency Mechanisms

The Python backend ensures data consistency through several mechanisms:

#### 1. **Idempotency Keys**
```python
def create_appointment(payload: dict, idempotency_key: str = None) -> dict:
    """
    Prevents duplicate operations using idempotency keys.
    Same key + same payload = same result (no duplicates created)
    """
    if idempotency_key and idempotency_key in idempotency_keys:
        return idempotency_keys[idempotency_key]  # Return cached result
```

#### 2. **Atomic Operations**
```python
def update_appointment_status(appointment_id: str, new_status: str) -> dict:
    """
    Atomic status updates with validation:
    1. Validate appointment exists
    2. Validate status transition is valid
    3. Update in single operation
    4. Return updated object
    """
```

#### 3. **Conflict Detection**
```python
def detect_scheduling_conflicts(appointment: dict) -> List[dict]:
    """
    Prevents double-booking by checking:
    - Same doctor
    - Same date
    - Overlapping time slots
    """
```

#### 4. **Optimistic Locking Simulation**
```python
def ensure_data_integrity():
    """
    Simulates database-level consistency:
    - Unique ID constraints
    - Referential integrity
    - Transaction-like operations
    """
```

### Frontend-Backend Consistency

The React frontend maintains consistency through:

1. **Backend-Driven State**: All mutations go through backend APIs
2. **Optimistic Updates**: UI updates immediately, rolls back on failure
3. **Error Handling**: Comprehensive error recovery and user feedback
4. **Real-time Sync**: Automatic refresh after operations

This architecture ensures that the appointment data remains consistent across all operations while providing a responsive user experience.

## Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/ASTROYAL/appointment-scheduling-system.git
cd appointment-scheduling-system

# Install dependencies
npm install
pip install -r requirements.txt

# Start the application
python start.py
```

### Deployment
The application is configured for easy deployment on Vercel:

1. Fork/clone this repository
2. Connect to Vercel
3. Deploy automatically

## Live Demo
🔗 **Live Application**: [Coming Soon - Deploy to get your live link]

## Project Structure
```
├── EMR_Frontend_Assignment.jsx    # Main React frontend (Required)
├── appointment_service.py         # Backend service functions (Required)
├── app.py                        # Flask web server
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
├── vercel.json                   # Deployment configuration
└── README.md                     # This file
```

## Features
- ✅ Complete appointment CRUD operations
- ✅ Real-time dashboard metrics
- ✅ Conflict detection and validation
- ✅ Responsive design with TailwindCSS
- ✅ Error handling and recovery
- ✅ GraphQL-style query structure
- ✅ Data consistency mechanisms

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Frontend Components](#frontend-components)
- [Setup Instructions](#setup-instructions)
- [Usage Examples](#usage-examples)
- [Data Consistency Model](#data-consistency-model)
- [Testing Strategy](#testing-strategy)
- [Error Handling](#error-handling)
- [Contributing](#contributing)

## Overview

The Appointment Scheduling and Queue Management system enables healthcare providers to:

- **Schedule and manage patient appointments** with comprehensive validation
- **View appointments in a calendar timeline format** with real-time updates
- **Filter appointments by date, status, and doctor** with advanced filtering options
- **Detect and resolve scheduling conflicts** automatically
- **Update appointment statuses** with real-time UI synchronization
- **Handle edge cases** like overlapping appointments and empty states
- **Monitor dashboard metrics** for scheduling patterns and system usage

### Key Features

- ✅ **Real-time Updates**: All appointment changes are immediately reflected across the interface
- ✅ **Conflict Detection**: Automatic detection of overlapping appointments for the same doctor
- ✅ **Data Consistency**: Idempotency keys prevent duplicate operations
- ✅ **Error Handling**: Comprehensive error handling with user-friendly messages
- ✅ **Property-Based Testing**: Extensive test coverage using hypothesis for Python
- ✅ **Responsive Design**: TailwindCSS-based responsive interface
- ✅ **Dashboard Analytics**: Comprehensive metrics and scheduling pattern analysis

## Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Client  │◄──►│  Backend Service │◄──►│  Data Storage   │
│  (Frontend)     │    │   (Python)       │    │ (Mock/PostgreSQL)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Technology Stack

- **Backend**: Python 3.x with type hints and comprehensive validation
- **Frontend**: React with hooks and modern JavaScript
- **Styling**: TailwindCSS for responsive design
- **Testing**: Hypothesis for property-based testing, pytest for unit tests
- **Data**: PostgreSQL simulation using Python dictionaries (production-ready structure)

### Data Flow Architecture

1. **Frontend Request**: React components call backend service functions directly
2. **Backend Processing**: Python functions validate input and perform business logic
3. **Data Operations**: Mock data store operations (simulating PostgreSQL transactions)
4. **Response Handling**: Results returned to frontend with standardized error handling
5. **UI Updates**: State changes trigger React re-renders with real-time updates

## API Reference

The backend service provides GraphQL-style query contracts with standardized input/output formats.

### Core Operations

#### Query Operations

##### `get_appointments(filters?: AppointmentFilters): Appointment[]`

Retrieve appointments with optional filtering support.

**Input Schema:**
```python
AppointmentFilters = {
    "date": "string?",        # YYYY-MM-DD format
    "status": "string?",      # Confirmed | Scheduled | Upcoming | Cancelled
    "doctorName": "string?"   # Doctor's full name
}
```

**Output Schema:**
```python
Appointment = {
    "id": "string",           # Unique identifier (apt_xxxxxxxx)
    "patientName": "string",  # Patient's full name
    "date": "string",         # YYYY-MM-DD format
    "time": "string",         # HH:MM format (24-hour)
    "duration": "number",     # Duration in minutes
    "doctorName": "string",   # Doctor's full name
    "status": "string",       # Confirmed | Scheduled | Upcoming | Cancelled
    "mode": "string"          # online | in-person
}
```

**Example Usage:**
```python
# Get all appointments
appointments = get_appointments()

# Get appointments for specific date
appointments = get_appointments({"date": "2024-01-15"})

# Get appointments for specific doctor and status
appointments = get_appointments({
    "doctorName": "Dr. Johnson",
    "status": "Confirmed"
})
```

##### `get_appointment_by_id(id: string): Appointment | null`

Retrieve a single appointment by its unique identifier.

**Input:** Appointment ID string
**Output:** Appointment object or null if not found

**Example Usage:**
```python
appointment = get_appointment_by_id("apt_001")
```

#### Mutation Operations

##### `create_appointment(payload: CreateAppointmentInput, idempotency_key?: string): Appointment`

Create a new appointment with validation and conflict detection.

**Input Schema:**
```python
CreateAppointmentInput = {
    "patientName": "string",    # Required: Patient's full name
    "date": "string",           # Required: YYYY-MM-DD format
    "time": "string",           # Required: HH:MM format (24-hour)
    "duration": "number",       # Required: Duration in minutes (1-480)
    "doctorName": "string",     # Required: Doctor's full name
    "mode": "string"            # Required: online | in-person
}
```

**Output:** Complete Appointment object with generated ID and default status "Scheduled"

**Error Conditions:**
- `ValidationError`: Missing or invalid required fields
- `ConflictError`: Scheduling conflict detected with existing appointment
- `NetworkError`: Simulated network failure (for testing)

**Example Usage:**
```python
new_appointment = create_appointment({
    "patientName": "John Smith",
    "date": "2024-01-15",
    "time": "09:00",
    "duration": 30,
    "doctorName": "Dr. Johnson",
    "mode": "in-person"
})
```

##### `update_appointment_status(id: string, new_status: string, idempotency_key?: string): Appointment`

Update the status of an existing appointment.

**Input:**
- `id`: Appointment identifier
- `new_status`: One of "Confirmed" | "Scheduled" | "Upcoming" | "Cancelled"
- `idempotency_key`: Optional key to prevent duplicate operations

**Output:** Updated Appointment object

**Error Conditions:**
- `NotFoundError`: Appointment ID does not exist
- `ValidationError`: Invalid status value
- `ConcurrencyError`: Concurrent modification detected

**Example Usage:**
```python
updated_appointment = update_appointment_status("apt_001", "Confirmed")
```

##### `delete_appointment(id: string): boolean`

Delete an appointment from the system.

**Input:** Appointment ID string
**Output:** Boolean indicating success (true) or failure (false)

**Example Usage:**
```python
success = delete_appointment("apt_001")
```

### Advanced Operations

#### `get_appointments_with_overlap_detection(filters?: ExtendedFilters): AppointmentQueryResult`

Enhanced appointment retrieval with overlap detection and metadata.

**Input Schema:**
```python
ExtendedFilters = {
    "date": "string?",
    "status": "string?", 
    "doctorName": "string?",
    "start_date": "string?",    # For date range queries
    "end_date": "string?"       # For date range queries
}
```

**Output Schema:**
```python
AppointmentQueryResult = {
    "appointments": "Appointment[]",
    "overlaps": "Dict[string, Appointment[]]",
    "empty_state": "EmptyStateMessages",
    "metadata": {
        "total_count": "number",
        "has_overlaps": "boolean",
        "overlap_count": "number",
        "unique_dates": "number",
        "unique_doctors": "number",
        "applied_filters": "ExtendedFilters"
    }
}
```

#### `get_dashboard_metrics(): DashboardMetrics`

Retrieve comprehensive dashboard metrics and scheduling analytics.

**Output Schema:**
```python
DashboardMetrics = {
    "totalAppointments": "number",
    "statusCounts": {
        "Confirmed": "number",
        "Scheduled": "number", 
        "Upcoming": "number",
        "Cancelled": "number"
    },
    "modeCounts": {
        "online": "number",
        "in-person": "number"
    },
    "doctorCounts": "Dict[string, number]",
    "recentActivity": "ActivityItem[]",
    "schedulingPatterns": {
        "averageDuration": "number",
        "mostCommonDuration": "number",
        "peakHours": "number[]",
        "busyDays": "string[]"
    }
}
```

### Error Response Format

All API functions use standardized error handling with detailed error information:

```python
# Validation Error Example
{
    "error": "ValidationError",
    "message": "Validation failed: Patient name is required; Date must be in YYYY-MM-DD format",
    "field_errors": {
        "patientName": "Patient name is required",
        "date": "Date must be in YYYY-MM-DD format"
    }
}

# Conflict Error Example  
{
    "error": "ConflictError",
    "message": "Scheduling conflicts detected: Conflict with appointment apt_002 at 09:00",
    "conflicts": [
        {
            "id": "apt_002",
            "time": "09:00",
            "patientName": "Sarah Wilson"
        }
    ]
}
```

## Frontend Components

### Component Hierarchy

```
AppointmentManagementView (Main Container)
├── CalendarInterface
│   ├── TimelineGrid
│   ├── AppointmentCard
│   └── DateSelector
├── FilterPanel
│   ├── StatusTabs (Upcoming, Today, Past)
│   └── DoctorFilter
├── CreateAppointmentForm
├── DashboardMetrics
│   ├── MetricsWidgets
│   └── ActivitySummary
└── ErrorBoundary
```

### Key Components

#### `AppointmentManagementView`
Main container component managing global state and orchestrating all child components.

**State Management:**
```javascript
const [appointments, setAppointments] = useState([])
const [selectedDate, setSelectedDate] = useState(new Date())
const [activeTab, setActiveTab] = useState('Today')
const [filters, setFilters] = useState({})
const [showCreateForm, setShowCreateForm] = useState(false)
const [loading, setLoading] = useState(false)
const [error, setError] = useState(null)
```

#### `CalendarInterface`
Displays appointments in a timeline grid format with time slots and appointment cards.

**Features:**
- Timeline grid with hourly slots
- Appointment cards with patient information
- Drag-and-drop support (future enhancement)
- Overlap handling for multiple appointments per slot

#### `CreateAppointmentForm`
Modal form for creating new appointments with comprehensive validation.

**Validation Rules:**
- Patient name: Required, non-empty string
- Date: Required, YYYY-MM-DD format, not in the past
- Time: Required, HH:MM format (24-hour)
- Duration: Required, 1-480 minutes
- Doctor: Required, non-empty string
- Mode: Required, "online" or "in-person"

#### `DashboardMetrics`
Analytics dashboard showing appointment statistics and scheduling patterns.

**Metrics Displayed:**
- Total appointment counts by status
- Appointment mode distribution
- Doctor workload distribution
- Recent activity timeline
- Peak scheduling hours
- Busiest appointment days

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn package manager

### Backend Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd appointment-scheduling-system
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install testing dependencies:**
```bash
pip install pytest hypothesis
```

4. **Verify backend setup:**
```bash
python -c "from appointment_service import get_appointments; print('Backend setup successful')"
```

### Frontend Setup

1. **Install Node.js dependencies:**
```bash
npm install
# or
yarn install
```

2. **Install required packages:**
```bash
npm install react react-dom
npm install -D tailwindcss postcss autoprefixer
npm install -D @vitejs/plugin-react vite
```

3. **Initialize TailwindCSS:**
```bash
npx tailwindcss init -p
```

4. **Start development server:**
```bash
npm run dev
# or
yarn dev
```

### Testing Setup

1. **Run Python tests:**
```bash
# Run all tests
pytest

# Run property-based tests only
pytest -k "property"

# Run with coverage
pytest --cov=appointment_service
```

2. **Run frontend tests:**
```bash
npm test
# or
yarn test
```

### Production Deployment

For production deployment, the system is designed to integrate with:

- **AWS AppSync** for GraphQL API management
- **Amazon Aurora PostgreSQL** for data persistence
- **AWS Lambda** for serverless backend functions
- **Amazon CloudFront** for frontend distribution
- **AWS Cognito** for authentication (future enhancement)

## Usage Examples

### Basic Appointment Management

```python
# Import the backend service
from appointment_service import (
    get_appointments, 
    create_appointment, 
    update_appointment_status,
    delete_appointment
)

# Get all appointments
all_appointments = get_appointments()
print(f"Total appointments: {len(all_appointments)}")

# Filter appointments by date
today_appointments = get_appointments({"date": "2024-01-15"})
print(f"Today's appointments: {len(today_appointments)}")

# Create a new appointment
new_appointment = create_appointment({
    "patientName": "Alice Johnson",
    "date": "2024-01-16", 
    "time": "14:30",
    "duration": 45,
    "doctorName": "Dr. Smith",
    "mode": "online"
})
print(f"Created appointment: {new_appointment['id']}")

# Update appointment status
updated = update_appointment_status(new_appointment['id'], "Confirmed")
print(f"Updated status: {updated['status']}")

# Delete appointment
success = delete_appointment(new_appointment['id'])
print(f"Deletion successful: {success}")
```

### Advanced Filtering and Analytics

```python
from appointment_service import (
    get_appointments_with_overlap_detection,
    get_dashboard_metrics,
    get_appointment_conflicts_summary
)

# Get appointments with overlap detection
result = get_appointments_with_overlap_detection({
    "start_date": "2024-01-15",
    "end_date": "2024-01-20"
})

print(f"Found {result['metadata']['total_count']} appointments")
print(f"Overlaps detected: {result['metadata']['has_overlaps']}")

# Get dashboard metrics
metrics = get_dashboard_metrics()
print(f"Total appointments: {metrics['totalAppointments']}")
print(f"Confirmed: {metrics['statusCounts']['Confirmed']}")
print(f"Average duration: {metrics['schedulingPatterns']['averageDuration']} minutes")

# Get conflict summary
conflicts = get_appointment_conflicts_summary("2024-01-15")
print(f"Conflicts found: {conflicts['total_conflicts']}")
for recommendation in conflicts['recommendations']:
    print(f"- {recommendation}")
```

### Frontend Integration

```javascript
import { 
  get_appointments, 
  create_appointment, 
  update_appointment_status 
} from './appointment_service.py';

// Load appointments with error handling
const loadAppointments = async () => {
  try {
    const appointments = await get_appointments({
      date: selectedDate,
      status: activeFilter
    });
    setAppointments(appointments);
  } catch (error) {
    console.error('Failed to load appointments:', error);
    setError('Failed to load appointments. Please try again.');
  }
};

// Create appointment with validation
const handleCreateAppointment = async (formData) => {
  try {
    const newAppointment = await create_appointment(formData);
    setAppointments(prev => [...prev, newAppointment]);
    setShowCreateForm(false);
    setSuccess('Appointment created successfully!');
  } catch (error) {
    if (error.message.includes('Validation failed')) {
      setValidationErrors(parseValidationErrors(error.message));
    } else if (error.message.includes('conflict')) {
      setError('Scheduling conflict detected. Please choose a different time.');
    } else {
      setError('Failed to create appointment. Please try again.');
    }
  }
};

// Update status with optimistic updates
const handleStatusUpdate = async (appointmentId, newStatus) => {
  // Optimistic update
  setAppointments(prev => 
    prev.map(apt => 
      apt.id === appointmentId 
        ? { ...apt, status: newStatus }
        : apt
    )
  );

  try {
    const updated = await update_appointment_status(appointmentId, newStatus);
    // Confirm the update
    setAppointments(prev => 
      prev.map(apt => 
        apt.id === appointmentId ? updated : apt
      )
    );
  } catch (error) {
    // Revert optimistic update on error
    loadAppointments();
    setError('Failed to update appointment status.');
  }
};
```

## Data Consistency Model

### Update Consistency Architecture

The system implements a **backend-driven consistency model** where all data mutations flow through the backend service to ensure data integrity and consistency.

#### Key Principles

1. **Single Source of Truth**: The backend service maintains the authoritative state
2. **No Local Mutations**: Frontend never modifies local state without backend confirmation
3. **Optimistic Updates**: UI updates optimistically but reverts on backend failure
4. **Idempotency**: All operations support idempotency keys to prevent duplicates
5. **Conflict Resolution**: Automatic detection and resolution of scheduling conflicts

#### Consistency Guarantees

```python
# Idempotency Example
idempotency_key = "create_apt_20240115_001"
appointment1 = create_appointment(payload, idempotency_key)
appointment2 = create_appointment(payload, idempotency_key)
# appointment1.id == appointment2.id (same appointment returned)

# Conflict Detection Example
appointment_data = {
    "patientName": "John Doe",
    "date": "2024-01-15",
    "time": "09:00",
    "duration": 30,
    "doctorName": "Dr. Johnson",
    "mode": "in-person"
}

# This will succeed
first_appointment = create_appointment(appointment_data)

# This will raise ConflictError due to overlapping time
overlapping_data = {**appointment_data, "patientName": "Jane Doe"}
try:
    second_appointment = create_appointment(overlapping_data)
except ValueError as e:
    print(f"Conflict detected: {e}")
```

#### Transaction Simulation

The current implementation simulates database transactions using Python data structures. In production, this would be replaced with actual PostgreSQL transactions:

```python
# Current Implementation (Mock)
def create_appointment(payload):
    # Validation
    validate_appointment_data(payload)
    
    # Conflict detection
    conflicts = detect_scheduling_conflicts(payload)
    if conflicts:
        raise ValueError("Scheduling conflicts detected")
    
    # Create appointment
    new_appointment = {**payload, "id": generate_unique_id()}
    appointments_db.append(new_appointment)
    return new_appointment

# Production Implementation (PostgreSQL)
def create_appointment(payload):
    with database.transaction():
        # Validation
        validate_appointment_data(payload)
        
        # Conflict detection with row locking
        conflicts = detect_scheduling_conflicts_with_lock(payload)
        if conflicts:
            raise ConflictError("Scheduling conflicts detected")
        
        # Insert with ACID guarantees
        new_appointment = database.insert_appointment(payload)
        return new_appointment
```

### Error Recovery Strategies

1. **Network Failures**: Automatic retry with exponential backoff
2. **Validation Errors**: Immediate user feedback with field-specific messages
3. **Conflict Errors**: Suggest alternative time slots
4. **Concurrency Errors**: Refresh data and prompt user to retry
5. **System Errors**: Graceful degradation with fallback values

## Testing Strategy

### Comprehensive Testing Approach

The system employs a dual testing strategy combining unit tests and property-based tests for maximum coverage and correctness validation.

#### Property-Based Testing

Using the `hypothesis` library, the system includes 15 core properties that validate universal behaviors:

```python
# Example Property Test
@given(st.text(min_size=1), st.dates(), st.times(), st.integers(min_value=1, max_value=480))
def test_appointment_creation_completeness(patient_name, date, time, duration):
    """Property 5: Appointment creation completeness"""
    appointment_data = {
        "patientName": patient_name.strip(),
        "date": date.strftime("%Y-%m-%d"),
        "time": time.strftime("%H:%M"),
        "duration": duration,
        "doctorName": "Dr. Test",
        "mode": "in-person"
    }
    
    if validate_appointment_data(appointment_data):
        result = create_appointment(appointment_data)
        
        # Verify all properties hold
        assert result["id"] is not None
        assert result["status"] == "Scheduled"
        assert result["patientName"] == appointment_data["patientName"]
        assert result["date"] == appointment_data["date"]
```

#### Unit Testing

Focused unit tests cover specific scenarios and edge cases:

```python
def test_empty_appointment_list():
    """Test handling of empty appointment scenarios"""
    global appointments_db
    original_db = appointments_db.copy()
    appointments_db.clear()
    
    try:
        result = get_appointments()
        assert result == []
        
        empty_state = handle_empty_appointment_scenarios()
        assert "no_appointments" in empty_state
        assert len(empty_state["suggestions"]) > 0
    finally:
        appointments_db = original_db

def test_overlapping_appointment_display():
    """Test proper handling of overlapping appointments"""
    overlapping_appointments = [
        {
            "id": "apt_test1",
            "date": "2024-01-15",
            "time": "09:00",
            "duration": 60,
            "doctorName": "Dr. Test"
        },
        {
            "id": "apt_test2", 
            "date": "2024-01-15",
            "time": "09:30",
            "duration": 60,
            "doctorName": "Dr. Test"
        }
    ]
    
    overlaps = get_overlapping_appointments(overlapping_appointments)
    assert len(overlaps) > 0
```

#### Integration Testing

End-to-end tests validate complete workflows:

```python
def test_complete_appointment_workflow():
    """Test complete appointment lifecycle"""
    # Create appointment
    appointment_data = {
        "patientName": "Integration Test Patient",
        "date": "2024-01-15",
        "time": "10:00", 
        "duration": 30,
        "doctorName": "Dr. Integration",
        "mode": "online"
    }
    
    created = create_appointment(appointment_data)
    assert created["id"] is not None
    
    # Retrieve appointment
    retrieved = get_appointment_by_id(created["id"])
    assert retrieved is not None
    assert retrieved["patientName"] == appointment_data["patientName"]
    
    # Update status
    updated = update_appointment_status(created["id"], "Confirmed")
    assert updated["status"] == "Confirmed"
    
    # Delete appointment
    success = delete_appointment(created["id"])
    assert success is True
    
    # Verify deletion
    deleted = get_appointment_by_id(created["id"])
    assert deleted is None
```

### Running Tests

```bash
# Run all tests
pytest

# Run property-based tests with verbose output
pytest -v -k "property"

# Run tests with coverage report
pytest --cov=appointment_service --cov-report=html

# Run specific test categories
pytest -m "unit"        # Unit tests only
pytest -m "property"    # Property tests only  
pytest -m "integration" # Integration tests only

# Run tests with hypothesis statistics
pytest --hypothesis-show-statistics
```

## Error Handling

### Comprehensive Error Management

The system implements multi-layered error handling with specific error types and recovery strategies.

#### Error Type Hierarchy

```python
class AppointmentError(Exception):
    """Base exception for appointment-related errors"""
    pass

class ValidationError(AppointmentError):
    """Raised when input validation fails"""
    def __init__(self, message, field_errors=None):
        super().__init__(message)
        self.field_errors = field_errors or {}

class ConflictError(AppointmentError):
    """Raised when scheduling conflicts are detected"""
    pass

class NetworkError(AppointmentError):
    """Raised for network-related failures"""
    pass

class ConcurrencyError(AppointmentError):
    """Raised when concurrent operations conflict"""
    pass
```

#### Frontend Error Handling

```javascript
// Enhanced error parsing and user feedback
const handleApiError = (error) => {
  if (error instanceof ValidationError) {
    // Show field-specific validation errors
    setFieldErrors(error.fieldErrors);
    setError('Please correct the highlighted fields.');
  } else if (error instanceof ConflictError) {
    // Show conflict resolution options
    setError('Scheduling conflict detected. Please choose a different time.');
    setSuggestedTimes(error.suggestedAlternatives);
  } else if (error instanceof NetworkError) {
    // Show retry options
    setError('Network error. Please check your connection and try again.');
    setShowRetryButton(true);
  } else if (error instanceof ConcurrencyError) {
    // Refresh data and show conflict message
    loadAppointments();
    setError('Another user modified this appointment. Please try again.');
  } else {
    // Generic error handling
    setError('An unexpected error occurred. Please try again.');
  }
};

// Retry mechanism with exponential backoff
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries || !isRetryableError(error)) {
        throw error;
      }
      
      const delay = Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};
```

#### Error Recovery Patterns

1. **Optimistic Updates with Rollback**
```javascript
const updateAppointmentStatus = async (id, newStatus) => {
  // Optimistic update
  setAppointments(prev => 
    prev.map(apt => apt.id === id ? {...apt, status: newStatus} : apt)
  );
  
  try {
    await update_appointment_status(id, newStatus);
  } catch (error) {
    // Rollback on failure
    loadAppointments();
    handleApiError(error);
  }
};
```

2. **Graceful Degradation**
```javascript
const loadDashboardMetrics = async () => {
  try {
    const metrics = await get_dashboard_metrics();
    setMetrics(metrics);
  } catch (error) {
    // Degrade gracefully with default values
    setMetrics({
      totalAppointments: 0,
      statusCounts: { Confirmed: 0, Scheduled: 0, Upcoming: 0, Cancelled: 0 },
      message: 'Metrics temporarily unavailable'
    });
  }
};
```

3. **Circuit Breaker Pattern**
```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.threshold = threshold;
    this.timeout = timeout;
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
  }
  
  async call(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }
  
  onFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.failureCount >= this.threshold) {
      this.state = 'OPEN';
    }
  }
}
```

## Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 for Python, ESLint configuration for JavaScript
2. **Testing**: All new features must include both unit tests and property-based tests
3. **Documentation**: Update README and inline documentation for any API changes
4. **Error Handling**: Implement comprehensive error handling with user-friendly messages
5. **Performance**: Consider performance implications for large appointment datasets

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Implement your feature
5. Ensure all tests pass (`pytest && npm test`)
6. Update documentation as needed
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Architecture Decisions

#### Backend Service Design

**Decision**: Use direct function imports instead of HTTP API calls
**Rationale**: Simulates GraphQL/AppSync integration while maintaining simplicity for development and testing
**Trade-offs**: Easier testing and development, but requires refactoring for production deployment

#### Data Consistency Model

**Decision**: Backend-driven state management with no local mutations
**Rationale**: Ensures data consistency and prevents state synchronization issues
**Trade-offs**: Slightly higher network overhead, but significantly better data integrity

#### Error Handling Strategy

**Decision**: Comprehensive error typing with specific recovery strategies
**Rationale**: Provides better user experience and easier debugging
**Trade-offs**: More complex error handling code, but much better user experience

#### Testing Approach

**Decision**: Dual testing strategy with property-based and unit tests
**Rationale**: Property-based tests catch edge cases, unit tests verify specific behaviors
**Trade-offs**: Longer test execution time, but significantly higher confidence in correctness

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions, please:

1. Check the [Issues](../../issues) page for existing problems
2. Create a new issue with detailed description and reproduction steps
3. For urgent matters, contact the development team

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Maintainers**: EMR Development Team