const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: false,
            errorMessage: '',
            form: {
                jobTitle: '',
                description: '',
                minCgpa: '',
                graduationYear: '',
                departments: '',
                packageSalary: '',
                location: '',
                deadline: ''
            }
        }
    },
    methods: {
        async saveDrive() {
            this.loading = true;
            this.errorMessage = '';
            const token = localStorage.getItem('access_token');

            try {
                const response = await fetch('/api/company/create_drive', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.form)
                });

                const data = await response.json();

                if (response.ok) {
                    alert("Drive Created Successfully! It is now pending Admin approval.");
                    window.location.href = '/company_dashboard';
                } else {
                    this.errorMessage = data.error || "Failed to create drive.";
                }
            } catch (error) {
                this.errorMessage = "Server error. Please try again later.";
            } finally {
                this.loading = false;
            }
        }
    }
}).mount('#app');