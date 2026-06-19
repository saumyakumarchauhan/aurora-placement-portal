const { createApp } = Vue;

createApp({
    data() {
        return {
            studentName: "Loading...",
            activeCompanies: [],
            myApplications: [],
            searchQuery: "",
        };
    },
    computed: {
        filteredCompanies() {
            if (!this.searchQuery) return this.activeCompanies;
            const query = this.searchQuery.toLowerCase();
            return this.activeCompanies.filter((comp) =>
                comp.name.toLowerCase().includes(query)
            );
        },
    },
    mounted() {
        this.fetchDashboardData();
    },
    methods: {
        getHeaders() {
            const token = localStorage.getItem("access_token");
            if (!token) window.location.href = "/login";
            return {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            };
        },

        async fetchDashboardData() {
            try {
                const response = await fetch("/api/student/data", {
                    method: "GET",
                    headers: this.getHeaders(),
                });

                if (response.status === 401 || response.status === 403) {
                    window.location.href = "/login";
                    return;
                }

                const data = await response.json();
                if (response.ok) {
                    this.studentName = data.studentName;
                    this.activeCompanies = data.activeCompanies;
                    this.myApplications = data.myApplications;
                }
            } catch (error) {
                console.error("Error fetching student data:", error);
            }
        },

        viewDetails(companyId) {
            window.location.href = `/student_view_company_details?id=${companyId}`;
        },

        // Updated to use Aurora Glass badge classes
        getStatusClass(status) {
            if (status === "Applied") return "is-info";
            if (status === "Shortlisted" || status === "Short Listed") return "is-warning";
            if (status === "Rejected") return "is-danger";
            if (status === "Selected") return "is-success";
            return "";
        },
    },
}).mount("#app");