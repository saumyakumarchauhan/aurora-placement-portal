const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: true,
            exporting: false,
            studentName: 'Loading...',
            department: 'Loading...',
            historyList: []
        }
    },
    mounted() {
        this.fetchHistory();
    },
    methods: {
        getHeaders() {
            const token = localStorage.getItem('access_token');
            if (!token) window.location.href = '/login';
            return {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            };
        },
        
        async fetchHistory() {
            try {
                const response = await fetch('/api/student/history', {
                    headers: this.getHeaders()
                });
                
                if (response.status === 401 || response.status === 403) {
                    window.location.href = '/login';
                    return;
                }

                if (response.ok) {
                    const data = await response.json();
                    this.studentName = data.studentName;
                    this.department = data.department;
                    this.historyList = data.historyList;
                    this.loading = false;
                } else {
                    alert("Failed to load history.");
                }
            } catch (error) {
                console.error("Error fetching history:", error);
            }
        },
        
        // Connects to your Celery task
        async exportHistory() {
            this.exporting = true;
            try {
                const response = await fetch('/api/student/export_history', {
                    method: 'POST',
                    headers: this.getHeaders()
                });
                
                const data = await response.json();
                
                if (response.status === 202) {
                    alert(data.message); // Will show "Export started..."
                } else {
                    alert(data.error || "Failed to start export.");
                }
            } catch (error) {
                alert("Server error connecting to background task.");
            } finally {
                this.exporting = false;
            }
        },
        
        // Updated to use the new Aurora Glass design system classes
        getStatusClass(status) {
            if (status === 'Applied') return 'is-info';
            if (status === 'Short Listed' || status === 'Shortlisted') return 'is-warning';
            if (status === 'Rejected') return 'is-danger';
            if (status === 'Selected') return 'is-success';
            return '';
        }
    }
}).mount('#app');