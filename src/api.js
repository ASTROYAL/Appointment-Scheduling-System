// API service for communicating with the Flask backend

const API_BASE_URL = '/api';

class APIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

const handleResponse = async (response) => {
  const data = await response.json();
  
  if (!response.ok) {
    throw new APIError(
      data.error || `HTTP ${response.status}`,
      response.status,
      data
    );
  }
  
  return data;
};

// Appointment API functions that match the Python backend
export const appointmentAPI = {
  // Get all appointments with optional filtering
  async getAppointments(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    
    const response = await fetch(`${API_BASE_URL}/appointments?${params}`);
    const result = await handleResponse(response);
    return result.data;
  },

  // Get single appointment by ID
  async getAppointmentById(id) {
    const response = await fetch(`${API_BASE_URL}/appointments/${id}`);
    const result = await handleResponse(response);
    return result.data;
  },

  // Create new appointment
  async createAppointment(appointmentData, idempotencyKey = null) {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }

    const response = await fetch(`${API_BASE_URL}/appointments`, {
      method: 'POST',
      headers,
      body: JSON.stringify(appointmentData),
    });
    
    const result = await handleResponse(response);
    return result.data;
  },

  // Update appointment status
  async updateAppointmentStatus(id, newStatus, idempotencyKey = null) {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }

    const response = await fetch(`${API_BASE_URL}/appointments/${id}/status`, {
      method: 'PUT',
      headers,
      body: JSON.stringify({ status: newStatus }),
    });
    
    const result = await handleResponse(response);
    return result.data;
  },

  // Delete appointment
  async deleteAppointment(id) {
    const response = await fetch(`${API_BASE_URL}/appointments/${id}`, {
      method: 'DELETE',
    });
    
    const result = await handleResponse(response);
    return result.success;
  },

  // Get dashboard metrics
  async getDashboardMetrics() {
    const response = await fetch(`${API_BASE_URL}/dashboard/metrics`);
    const result = await handleResponse(response);
    return result.data;
  },

  // Get appointments with overlap detection
  async getAppointmentsWithOverlaps(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    
    const response = await fetch(`${API_BASE_URL}/appointments/overlaps?${params}`);
    const result = await handleResponse(response);
    return result.data;
  }
};

// Export individual functions to match the Python import style
export const {
  getAppointments,
  getAppointmentById,
  createAppointment,
  updateAppointmentStatus,
  deleteAppointment,
  getDashboardMetrics,
  getAppointmentsWithOverlaps
} = appointmentAPI;

// Default export
export default appointmentAPI;