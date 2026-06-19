const { createApp } = Vue;

createApp({
    data() {
        return {
            stats: {
                total_drives: 0,
                total_apps: 0,
                total_selected: 0,
                pending_drives: 0,
            },
            registeredCompanies: [],
            registeredStudents: [],
            companyApplications: [],
            ongoingDrives: [],
            studentApplications: [],
            searchQuery: "",
        };
    },

    computed: {
        filteredCompanies() {
            if (!this.searchQuery) return this.registeredCompanies;
            return this.registeredCompanies.filter((c) =>
                c.name.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        },
        filteredStudents() {
            if (!this.searchQuery) return this.registeredStudents;
            return this.registeredStudents.filter((s) =>
                s.name.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        },
        filteredDrives() {
            if (!this.searchQuery) return this.ongoingDrives;
            const q = this.searchQuery.toLowerCase();
            return this.ongoingDrives.filter(
                (d) =>
                    d.name.toLowerCase().includes(q) ||
                    d.company.toLowerCase().includes(q)
            );
        },
    },

    mounted() {
        this.fetchDashboardData();
        this.fetchStats();
    },

    methods: {
        getHeaders() {
            const token = localStorage.getItem("access_token");
            if (!token) {
                window.location.href = "/login";
            }
            return {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            };
        },

        async fetchDashboardData() {
            try {
                const response = await fetch("/api/admin/data", {
                    method: "GET",
                    headers: this.getHeaders(),
                });

                if (response.status === 401 || response.status === 403) {
                    window.location.href = "/login";
                    return;
                }

                const data = await response.json();
                if (response.ok) {
                    this.registeredCompanies = data.registeredCompanies;
                    this.companyApplications = data.companyApplications;
                    this.registeredStudents = data.registeredStudents;
                    this.ongoingDrives = data.ongoingDrives;
                    this.studentApplications = data.studentApplications;
                }
            } catch (error) {
                console.error("Error fetching admin data:", error);
            }
        },

        async fetchStats() {
            try {
                const res = await fetch("/api/admin/stats", {
                    headers: this.getHeaders(),
                });
                if (res.ok) {
                    const data = await res.json();
                    this.stats = data;
                }
            } catch (e) {
                console.error("Stats fail");
            }
        },

        async triggerJob(type) {
            if (confirm(`Trigger ${type} job? This will process in background.`)) {
                try {
                    const res = await fetch(`/api/admin/trigger_jobs/${type}`, {
                        method: "POST",
                        headers: this.getHeaders(),
                    });
                    const data = await res.json();
                    alert(data.message || "Job triggered successfully!");
                } catch (e) {
                    alert("Job failed to trigger");
                }
            }
        },

        async approveCompany(company) {
            if (confirm(`Approve registration for ${company.name}?`)) {
                const response = await fetch(
                    `/api/admin/approve_company/${company.id}`,
                    {
                        method: "POST",
                        headers: this.getHeaders(),
                    }
                );
                if (response.ok) {
                    this.fetchDashboardData();
                    alert("Company Approved!");
                }
            }
        },

        async blacklistCompany(company) {
            if (confirm(`Blacklist ${company.name}?`)) {
                const response = await fetch(`/api/admin/blacklist/${company.id}`, {
                    method: "POST",
                    headers: this.getHeaders(),
                });
                if (response.ok) this.fetchDashboardData();
            }
        },

        async blacklistStudent(student) {
            if (confirm(`Blacklist ${student.name}?`)) {
                const response = await fetch(`/api/admin/blacklist/${student.id}`, {
                    method: "POST",
                    headers: this.getHeaders(),
                });
                if (response.ok) this.fetchDashboardData();
            }
        },

        async approveDrive(drive) {
            if (confirm(`Approve drive: ${drive.name}?`)) {
                const res = await fetch(`/api/admin/approve_drive/${drive.id}`, {
                    method: "POST",
                    headers: this.getHeaders(),
                });
                if (res.ok) {
                    this.fetchDashboardData();
                    this.fetchStats();
                }
            }
        },

        async markComplete(drive) {
            if (confirm(`Mark '${drive.name}' as complete?`)) {
                const response = await fetch(
                    `/api/admin/mark_drive_complete/${drive.id}`,
                    {
                        method: "POST",
                        headers: this.getHeaders(),
                    }
                );
                if (response.ok) this.fetchDashboardData();
            }
        },

        viewDrive(drive) {
            window.location.href = `/admin_view_drive_details?id=${drive.id}`;
        },
        viewApp(app) {
            window.location.href = `/admin_view_student_application?id=${app.id}`;
        },
    },
}).mount("#app");