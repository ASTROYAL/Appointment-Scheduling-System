#!/usr/bin/env python3
"""
Flask Web Application for Appointment Scheduling System

This Flask app provides a REST API interface for the appointment scheduling system
and serves the React frontend.
"""

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import json
import traceback
from datetime import datetime, date
import os

# Import our appointment service
from appointment_service import (
    get_appointments,
    get_appointment_by_id,
    create_appointment,
    update_appointment_status,
    delete_appointment,
    get_dashboard_metrics,
    get_appointments_with_overlap_detection,
    AppointmentStatus,
    AppointmentMode
)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Error handling
class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

@app.errorhandler(APIError)
def handle_api_error(error):
    response = {'error': error.message}
    if error.payload:
        response.update(error.payload)
    return jsonify(response), error.status_code

@app.errorhandler(Exception)
def handle_general_error(error):
    app.logger.error(f"Unhandled error: {str(error)}")
    app.logger.error(traceback.format_exc())
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500

# API Routes

@app.route('/api/appointments', methods=['GET'])
def api_get_appointments():
    """Get appointments with optional filtering"""
    try:
        # Parse query parameters
        filters = {}
        if request.args.get('date'):
            filters['date'] = request.args.get('date')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('doctorName'):
            filters['doctorName'] = request.args.get('doctorName')
        
        # Get appointments
        appointments = get_appointments(filters)
        
        return jsonify({
            'success': True,
            'data': appointments,
            'count': len(appointments),
            'filters': filters
        })
    except Exception as e:
        raise APIError(f"Failed to get appointments: {str(e)}")

@app.route('/api/appointments/<appointment_id>', methods=['GET'])
def api_get_appointment(appointment_id):
    """Get a single appointment by ID"""
    try:
        appointment = get_appointment_by_id(appointment_id)
        if appointment is None:
            raise APIError(f"Appointment {appointment_id} not found", 404)
        
        return jsonify({
            'success': True,
            'data': appointment
        })
    except APIError:
        raise
    except Exception as e:
        raise APIError(f"Failed to get appointment: {str(e)}")

@app.route('/api/appointments', methods=['POST'])
def api_create_appointment():
    """Create a new appointment"""
    try:
        data = request.get_json()
        if not data:
            raise APIError("No data provided")
        
        # Extract idempotency key if provided
        idempotency_key = request.headers.get('Idempotency-Key')
        
        # Create appointment
        if idempotency_key:
            appointment = create_appointment(data, idempotency_key)
        else:
            appointment = create_appointment(data)
        
        return jsonify({
            'success': True,
            'data': appointment,
            'message': 'Appointment created successfully'
        }), 201
    except ValueError as e:
        raise APIError(str(e), 400)
    except Exception as e:
        raise APIError(f"Failed to create appointment: {str(e)}")

@app.route('/api/appointments/<appointment_id>/status', methods=['PUT'])
def api_update_appointment_status(appointment_id):
    """Update appointment status"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            raise APIError("Status is required")
        
        new_status = data['status']
        idempotency_key = request.headers.get('Idempotency-Key')
        
        # Update status
        if idempotency_key:
            appointment = update_appointment_status(appointment_id, new_status, idempotency_key)
        else:
            appointment = update_appointment_status(appointment_id, new_status)
        
        return jsonify({
            'success': True,
            'data': appointment,
            'message': f'Appointment status updated to {new_status}'
        })
    except ValueError as e:
        raise APIError(str(e), 400)
    except Exception as e:
        raise APIError(f"Failed to update appointment status: {str(e)}")

@app.route('/api/appointments/<appointment_id>', methods=['DELETE'])
def api_delete_appointment(appointment_id):
    """Delete an appointment"""
    try:
        success = delete_appointment(appointment_id)
        if not success:
            raise APIError(f"Appointment {appointment_id} not found", 404)
        
        return jsonify({
            'success': True,
            'message': 'Appointment deleted successfully'
        })
    except APIError:
        raise
    except Exception as e:
        raise APIError(f"Failed to delete appointment: {str(e)}")

@app.route('/api/dashboard/metrics', methods=['GET'])
def api_get_dashboard_metrics():
    """Get dashboard metrics and analytics"""
    try:
        metrics = get_dashboard_metrics()
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        raise APIError(f"Failed to get dashboard metrics: {str(e)}")

@app.route('/api/appointments/overlaps', methods=['GET'])
def api_get_appointments_with_overlaps():
    """Get appointments with overlap detection"""
    try:
        # Parse query parameters
        filters = {}
        if request.args.get('date'):
            filters['date'] = request.args.get('date')
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        if request.args.get('doctorName'):
            filters['doctorName'] = request.args.get('doctorName')
        
        result = get_appointments_with_overlap_detection(filters)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        raise APIError(f"Failed to get appointments with overlaps: {str(e)}")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Serve React Frontend
@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# HTML Template with embedded React app
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Appointment Scheduling System</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .appointment-card {
            transition: all 0.2s ease-in-out;
        }
        .appointment-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .status-confirmed { border-left: 4px solid #10b981; }
        .status-scheduled { border-left: 4px solid #3b82f6; }
        .status-upcoming { border-left: 4px solid #f59e0b; }
        .status-cancelled { border-left: 4px solid #ef4444; }
        
        .loading-spinner {
            border: 3px solid #f3f4f6;
            border-top: 3px solid #3b82f6;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-50">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // API utility functions
        const api = {
            async get(url) {
                const response = await fetch(`/api${url}`);
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Request failed');
                return data;
            },
            
            async post(url, body) {
                const response = await fetch(`/api${url}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Request failed');
                return data;
            },
            
            async put(url, body) {
                const response = await fetch(`/api${url}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Request failed');
                return data;
            },
            
            async delete(url) {
                const response = await fetch(`/api${url}`, { method: 'DELETE' });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Request failed');
                return data;
            }
        };

        // Main App Component
        function AppointmentApp() {
            const [appointments, setAppointments] = useState([]);
            const [loading, setLoading] = useState(true);
            const [error, setError] = useState(null);
            const [success, setSuccess] = useState(null);
            const [activeTab, setActiveTab] = useState('Today');
            const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
            const [showCreateForm, setShowCreateForm] = useState(false);
            const [metrics, setMetrics] = useState(null);

            // Load appointments
            const loadAppointments = async (filters = {}) => {
                try {
                    setLoading(true);
                    setError(null);
                    
                    const params = new URLSearchParams();
                    if (filters.date) params.append('date', filters.date);
                    if (filters.status) params.append('status', filters.status);
                    if (filters.doctorName) params.append('doctorName', filters.doctorName);
                    
                    const response = await api.get(`/appointments?${params}`);
                    setAppointments(response.data);
                } catch (err) {
                    setError(err.message);
                } finally {
                    setLoading(false);
                }
            };

            // Load dashboard metrics
            const loadMetrics = async () => {
                try {
                    const response = await api.get('/dashboard/metrics');
                    setMetrics(response.data);
                } catch (err) {
                    console.error('Failed to load metrics:', err);
                }
            };

            // Filter appointments by tab
            const getFilteredAppointments = () => {
                const today = new Date().toISOString().split('T')[0];
                
                switch (activeTab) {
                    case 'Today':
                        return appointments.filter(apt => apt.date === today);
                    case 'Upcoming':
                        return appointments.filter(apt => apt.date > today);
                    case 'Past':
                        return appointments.filter(apt => apt.date < today);
                    default:
                        return appointments;
                }
            };

            // Update appointment status
            const updateStatus = async (id, newStatus) => {
                try {
                    await api.put(`/appointments/${id}/status`, { status: newStatus });
                    setSuccess(`Appointment status updated to ${newStatus}`);
                    loadAppointments();
                } catch (err) {
                    setError(err.message);
                }
            };

            // Delete appointment
            const deleteAppointment = async (id) => {
                if (!confirm('Are you sure you want to delete this appointment?')) return;
                
                try {
                    await api.delete(`/appointments/${id}`);
                    setSuccess('Appointment deleted successfully');
                    loadAppointments();
                } catch (err) {
                    setError(err.message);
                }
            };

            // Create appointment
            const createAppointment = async (formData) => {
                try {
                    await api.post('/appointments', formData);
                    setSuccess('Appointment created successfully');
                    setShowCreateForm(false);
                    loadAppointments();
                } catch (err) {
                    setError(err.message);
                }
            };

            // Load data on mount
            useEffect(() => {
                loadAppointments();
                loadMetrics();
            }, []);

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

            const filteredAppointments = getFilteredAppointments();

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
                                <div className="bg-white rounded-lg shadow p-6">
                                    <h2 className="text-lg font-semibold text-gray-900 mb-4">
                                        Dashboard Metrics
                                    </h2>
                                    {metrics ? (
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
                                    ) : (
                                        <div className="flex items-center justify-center py-4">
                                            <div className="loading-spinner"></div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Main Content */}
                            <div className="lg:col-span-3">
                                {/* Tab Navigation */}
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
                                                    {tab !== 'All' && (
                                                        <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                                                            {getFilteredAppointments().length}
                                                        </span>
                                                    )}
                                                </button>
                                            ))}
                                        </nav>
                                    </div>
                                </div>

                                {/* Appointments List */}
                                <div className="bg-white rounded-lg shadow">
                                    <div className="px-6 py-4 border-b border-gray-200">
                                        <h2 className="text-lg font-semibold text-gray-900">
                                            {activeTab} Appointments ({filteredAppointments.length})
                                        </h2>
                                    </div>
                                    
                                    {loading ? (
                                        <div className="flex items-center justify-center py-12">
                                            <div className="loading-spinner"></div>
                                            <span className="ml-2 text-gray-600">Loading appointments...</span>
                                        </div>
                                    ) : filteredAppointments.length === 0 ? (
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
                                    ) : (
                                        <div className="divide-y divide-gray-200">
                                            {filteredAppointments.map(appointment => (
                                                <AppointmentCard
                                                    key={appointment.id}
                                                    appointment={appointment}
                                                    onUpdateStatus={updateStatus}
                                                    onDelete={deleteAppointment}
                                                />
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Create Appointment Modal */}
                    {showCreateForm && (
                        <CreateAppointmentModal
                            onClose={() => setShowCreateForm(false)}
                            onCreate={createAppointment}
                        />
                    )}
                </div>
            );
        }

        // Appointment Card Component
        function AppointmentCard({ appointment, onUpdateStatus, onDelete }) {
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
                <div className={`appointment-card p-6 status-${appointment.status.toLowerCase()}`}>
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
                                        className="text-green-600 hover:text-green-800 text-sm font-medium"
                                        title="Confirm appointment"
                                    >
                                        ✓
                                    </button>
                                )}
                                
                                {appointment.status !== 'Cancelled' && (
                                    <button
                                        onClick={() => onUpdateStatus(appointment.id, 'Cancelled')}
                                        className="text-red-600 hover:text-red-800 text-sm font-medium"
                                        title="Cancel appointment"
                                    >
                                        ✗
                                    </button>
                                )}
                                
                                <button
                                    onClick={() => onDelete(appointment.id)}
                                    className="text-gray-400 hover:text-red-600 text-sm font-medium"
                                    title="Delete appointment"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        // Create Appointment Modal
        function CreateAppointmentModal({ onClose, onCreate }) {
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
        }

        // Render the app
        ReactDOM.render(<AppointmentApp />, document.getElementById('root'));
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Starting Appointment Scheduling Web Application...")
    print("📊 Backend: Flask API with appointment service")
    print("🎨 Frontend: React with TailwindCSS")
    print("🔗 URL: http://localhost:5000")
    print("\n" + "="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)