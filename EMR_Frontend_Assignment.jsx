import { useEffect, useState } from 'react';

// API functions that communicate with the Python backend
// These simulate GraphQL-style queries but use REST API calls
const api = {
  async getAppointments(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    
    const response = await fetch(`/api/appointments?${params}`);
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to fetch appointments');
    return result.data;
  },

  async createAppointment(appointmentData) {
    const response = await fetch('/api/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appointmentData),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to create appointment');
    return result.data;
  },

  async updateAppointmentStatus(id, newStatus) {
    const response = await fetch(`/api/appointments/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to update status');
    return result.data;
  },

  async deleteAppointment(id) {
    const response = await fetch(`/api/appointments/${id}`, {
      method: 'DELETE',
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to delete appointment');
    return result.success;
  },

  async getDashboardMetrics() {
    const response = await fetch('/api/dashboard/metrics');
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to fetch metrics');
    return result.data;
  }
};

// Enhanced Error Handling Classes
class AppointmentError extends Error {
  constructor(message, type = 'general', details = {}) {
    super(message);
    this.name = 'AppointmentError';
    this.type = type;
    this.details = details;
  }
}

class NetworkError extends AppointmentError {
  constructor(message, details = {}) {
    super(message, 'network', details);
    this.name = 'NetworkError';
  }
}

class ValidationError extends AppointmentError {
  constructor(message, fieldErrors = {}) {
    super(message, 'validation', { fieldErrors });
    this.name = 'ValidationError';
    this.fieldErrors = fieldErrors;
  }
}

// Enhanced retry mechanism with exponential backoff
const retryWithBackoff = async (fn, maxRetries = 3, baseDelay = 1000) => {
  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Only retry on network errors
      if (error.message.includes('network') || 
          error.message.includes('timeout') ||
          error.message.includes('fetch')) {
        
        if (attempt < maxRetries) {
          // Exponential backoff with jitter
          const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }
      }
      
      throw error;
    }
  }
  
  throw lastError;
};

// Enhanced error parsing for backend responses
const parseBackendError = (error) => {
  if (error.message.includes('Validation failed:')) {
    const message = error.message.replace('Validation failed: ', '');
    const fieldErrors = {};
    
    // Parse field-specific errors from backend message
    const errorParts = message.split('; ');
    errorParts.forEach(part => {
      if (part.includes('name')) fieldErrors.patientName = part;
      if (part.includes('date')) fieldErrors.date = part;
      if (part.includes('time')) fieldErrors.time = part;
      if (part.includes('duration')) fieldErrors.duration = part;
      if (part.includes('doctor')) fieldErrors.doctorName = part;
      if (part.includes('mode')) fieldErrors.mode = part;
    });
    
    return new ValidationError(message, fieldErrors);
  }
  
  if (error.message.includes('network') || 
      error.message.includes('timeout') ||
      error.message.includes('fetch')) {
    return new NetworkError(error.message);
  }
  
  return new AppointmentError(error.message);
};

// Main Appointment Management Component
const AppointmentManagementView = () => {
  // State management for appointments, filters, and UI state
  const [appointments, setAppointments] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [activeTab, setActiveTab] = useState('Today');
  const [filters, setFilters] = useState({});
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [metrics, setMetrics] = useState(null);

  // Load appointments on component mount and when filters change
  useEffect(() => {
    loadAppointments();
    loadDashboardMetrics();
  }, [filters, selectedDate, activeTab]);

  // Auto-clear messages
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Load dashboard metrics
  const loadDashboardMetrics = async () => {
    try {
      const metricsData = await api.getDashboardMetrics();
      setMetrics(metricsData);
    } catch (err) {
      console.warn('Failed to load dashboard metrics:', err);
    }
  };

  // Load appointments using backend service with enhanced error handling
  const loadAppointments = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await retryWithBackoff(async () => {
        // Build filter object based on current state
        const currentFilters = {
          ...filters,
          ...(selectedDate && activeTab === 'Today' && { date: selectedDate })
        };

        const appointmentData = await api.getAppointments(currentFilters);
        
        // Apply client-side date filtering for Upcoming and Past tabs
        let filteredAppointments = appointmentData;
        const today = new Date().toISOString().split('T')[0];
        
        if (activeTab === 'Upcoming') {
          filteredAppointments = appointmentData.filter(apt => apt.date > today);
        } else if (activeTab === 'Past') {
          filteredAppointments = appointmentData.filter(apt => apt.date < today);
        } else if (activeTab === 'Today') {
          filteredAppointments = appointmentData.filter(apt => apt.date === today);
        }

        return filteredAppointments;
      }, 2, 1000);

      setAppointments(result);
    } catch (err) {
      const parsedError = parseBackendError(err);
      
      let errorMessage = 'Failed to load appointments';
      
      if (parsedError instanceof NetworkError) {
        errorMessage = `Network error: ${parsedError.message}. Please check your connection and try again.`;
      } else if (parsedError instanceof ValidationError) {
        errorMessage = `Invalid request: ${parsedError.message}`;
      } else {
        errorMessage = `${errorMessage}: ${parsedError.message}`;
      }
      
      setError(errorMessage);
      console.error('Load appointments error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Create new appointment with comprehensive error handling
  const handleCreateAppointment = async (appointmentData) => {
    try {
      setError(null);
      
      const result = await retryWithBackoff(async () => {
        return await api.createAppointment(appointmentData);
      }, 1, 1000);
      
      setSuccess('Appointment created successfully!');
      setShowCreateForm(false);
      
      // Refresh appointments list
      await loadAppointments();
      await loadDashboardMetrics();
      
    } catch (err) {
      const parsedError = parseBackendError(err);
      
      if (parsedError instanceof ValidationError) {
        setError(`Validation error: ${parsedError.message}`);
      } else if (parsedError instanceof NetworkError) {
        setError(`Network error: ${parsedError.message}. Please try again.`);
      } else if (parsedError.message.includes('conflict')) {
        setError(`Scheduling conflict: ${parsedError.message}. Please choose a different time.`);
      } else {
        setError(`Failed to create appointment: ${parsedError.message}`);
      }
      
      console.error('Create appointment error:', err);
    }
  };

  // Update appointment status with optimistic updates and rollback
  const handleUpdateAppointmentStatus = async (appointmentId, newStatus) => {
    // Optimistic update
    const originalAppointments = [...appointments];
    setAppointments(prev => 
      prev.map(apt => 
        apt.id === appointmentId 
          ? { ...apt, status: newStatus }
          : apt
      )
    );

    try {
      setError(null);
      
      await retryWithBackoff(async () => {
        return await api.updateAppointmentStatus(appointmentId, newStatus);
      }, 2, 1000);
      
      setSuccess(`Appointment status updated to ${newStatus}`);
      
      // Refresh to ensure consistency
      await loadAppointments();
      await loadDashboardMetrics();
      
    } catch (err) {
      // Rollback optimistic update
      setAppointments(originalAppointments);
      
      const parsedError = parseBackendError(err);
      
      if (parsedError instanceof NetworkError) {
        setError(`Network error: ${parsedError.message}. Status update failed.`);
      } else {
        setError(`Failed to update appointment status: ${parsedError.message}`);
      }
      
      console.error('Update status error:', err);
    }
  };

  // Delete appointment with confirmation
  const handleDeleteAppointment = async (appointmentId) => {
    if (!window.confirm('Are you sure you want to delete this appointment?')) {
      return;
    }

    try {
      setError(null);
      
      await retryWithBackoff(async () => {
        return await api.deleteAppointment(appointmentId);
      }, 2, 1000);
      
      setSuccess('Appointment deleted successfully');
      
      // Refresh appointments list
      await loadAppointments();
      await loadDashboardMetrics();
      
    } catch (err) {
      const parsedError = parseBackendError(err);
      
      if (parsedError instanceof NetworkError) {
        setError(`Network error: ${parsedError.message}. Delete failed.`);
      } else {
        setError(`Failed to delete appointment: ${parsedError.message}`);
      }
      
      console.error('Delete appointment error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Appointment Scheduling System
              </h1>
              <p className="text-gray-600 mt-1">
                Manage patient appointments and schedules
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              + New Appointment
            </button>
          </div>
        </div>
      </header>

      {/* Messages */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      )}
      
      {success && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Metrics */}
          <div className="lg:col-span-1">
            <DashboardMetrics metrics={metrics} />
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Tab Navigation */}
            <StatusTabs 
              activeTab={activeTab} 
              setActiveTab={setActiveTab}
              appointments={appointments}
            />

            {/* Appointments List */}
            <CalendarInterface
              appointments={appointments}
              loading={loading}
              activeTab={activeTab}
              onUpdateStatus={handleUpdateAppointmentStatus}
              onDelete={handleDeleteAppointment}
            />
          </div>
        </div>
      </div>

      {/* Create Appointment Modal */}
      {showCreateForm && (
        <CreateAppointmentForm
          onClose={() => setShowCreateForm(false)}
          onCreate={handleCreateAppointment}
        />
      )}
    </div>
  );
};

// Dashboard Metrics Component
const DashboardMetrics = ({ metrics }) => {
  if (!metrics) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Dashboard Metrics
        </h2>
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Dashboard Metrics
      </h2>
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-600">Total Appointments</p>
          <p className="text-2xl font-bold text-blue-600">
            {metrics.totalAppointments}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-2">Status Breakdown</p>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span>Confirmed:</span>
              <span className="font-medium">{metrics.statusCounts.Confirmed}</span>
            </div>
            <div className="flex justify-between">
              <span>Scheduled:</span>
              <span className="font-medium">{metrics.statusCounts.Scheduled}</span>
            </div>
            <div className="flex justify-between">
              <span>Upcoming:</span>
              <span className="font-medium">{metrics.statusCounts.Upcoming}</span>
            </div>
            <div className="flex justify-between">
              <span>Cancelled:</span>
              <span className="font-medium">{metrics.statusCounts.Cancelled}</span>
            </div>
          </div>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-2">Mode Distribution</p>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span>Online:</span>
              <span className="font-medium">{metrics.modeCounts.online}</span>
            </div>
            <div className="flex justify-between">
              <span>In-Person:</span>
              <span className="font-medium">{metrics.modeCounts['in-person']}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Status Tabs Component
const StatusTabs = ({ activeTab, setActiveTab, appointments }) => {
  const today = new Date().toISOString().split('T')[0];
  
  const getCounts = () => {
    return {
      Today: appointments.filter(apt => apt.date === today).length,
      Upcoming: appointments.filter(apt => apt.date > today).length,
      Past: appointments.filter(apt => apt.date < today).length,
      All: appointments.length
    };
  };

  const counts = getCounts();

  return (
    <div className="bg-white rounded-lg shadow mb-6">
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {['Today', 'Upcoming', 'Past', 'All'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab}
              <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                {counts[tab]}
              </span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
};

// Calendar Interface Component
const CalendarInterface = ({ appointments, loading, activeTab, onUpdateStatus, onDelete }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            {activeTab} Appointments
          </h2>
        </div>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading appointments...</span>
        </div>
      </div>
    );
  }

  if (appointments.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            {activeTab} Appointments (0)
          </h2>
        </div>
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📅</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No appointments found
          </h3>
          <p className="text-gray-600">
            {activeTab === 'Today' ? "No appointments scheduled for today." :
             activeTab === 'Upcoming' ? "No upcoming appointments." :
             activeTab === 'Past' ? "No past appointments." :
             "No appointments in the system."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          {activeTab} Appointments ({appointments.length})
        </h2>
      </div>
      
      <div className="divide-y divide-gray-200">
        {appointments.map(appointment => (
          <AppointmentCard
            key={appointment.id}
            appointment={appointment}
            onUpdateStatus={onUpdateStatus}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
};

// Appointment Card Component
const AppointmentCard = ({ appointment, onUpdateStatus, onDelete }) => {
  const statusColors = {
    'Confirmed': 'bg-green-100 text-green-800',
    'Scheduled': 'bg-blue-100 text-blue-800',
    'Upcoming': 'bg-yellow-100 text-yellow-800',
    'Cancelled': 'bg-red-100 text-red-800'
  };

  const modeIcons = {
    'online': '💻',
    'in-person': '🏥'
  };

  return (
    <div className={`p-6 hover:bg-gray-50 transition-colors border-l-4 ${
      appointment.status === 'Confirmed' ? 'border-green-500' :
      appointment.status === 'Scheduled' ? 'border-blue-500' :
      appointment.status === 'Upcoming' ? 'border-yellow-500' :
      'border-red-500'
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {appointment.patientName}
              </h3>
              <p className="text-sm text-gray-600">
                {modeIcons[appointment.mode]} {appointment.doctorName}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {appointment.date} at {appointment.time}
              </p>
              <p className="text-sm text-gray-600">
                {appointment.duration} minutes
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[appointment.status]}`}>
            {appointment.status}
          </span>
          
          <div className="flex space-x-1">
            {appointment.status !== 'Confirmed' && (
              <button
                onClick={() => onUpdateStatus(appointment.id, 'Confirmed')}
                className="text-green-600 hover:text-green-800 text-sm font-medium px-2 py-1 rounded"
                title="Confirm appointment"
              >
                ✓
              </button>
            )}
            
            {appointment.status !== 'Cancelled' && (
              <button
                onClick={() => onUpdateStatus(appointment.id, 'Cancelled')}
                className="text-red-600 hover:text-red-800 text-sm font-medium px-2 py-1 rounded"
                title="Cancel appointment"
              >
                ✗
              </button>
            )}
            
            <button
              onClick={() => onDelete(appointment.id)}
              className="text-gray-400 hover:text-red-600 text-sm font-medium px-2 py-1 rounded"
              title="Delete appointment"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Create Appointment Form Component
const CreateAppointmentForm = ({ onClose, onCreate }) => {
  const [formData, setFormData] = useState({
    patientName: '',
    date: new Date().toISOString().split('T')[0],
    time: '',
    duration: 30,
    doctorName: '',
    mode: 'in-person'
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onCreate(formData);
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Create New Appointment
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Patient Name
            </label>
            <input
              type="text"
              name="patientName"
              value={formData.patientName}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date
              </label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Time
              </label>
              <input
                type="time"
                name="time"
                value={formData.time}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Duration (minutes)
            </label>
            <select
              name="duration"
              value={formData.duration}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={45}>45 minutes</option>
              <option value={60}>1 hour</option>
              <option value={90}>1.5 hours</option>
              <option value={120}>2 hours</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Doctor Name
            </label>
            <input
              type="text"
              name="doctorName"
              value={formData.doctorName}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mode
            </label>
            <select
              name="mode"
              value={formData.mode}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="in-person">In-Person</option>
              <option value="online">Online</option>
            </select>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? 'Creating...' : 'Create Appointment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AppointmentManagementView;