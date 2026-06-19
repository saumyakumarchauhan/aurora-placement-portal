const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: true,
            companyId: null,
            studentName: "Loading...",
            company: { drives: [] },
        };
    },
    mounted() {
        const urlParams = new URLSearchParams(window.location.search);
        this.companyId = urlParams.get("id");
        if (this.companyId) {
            this.fetchCompanyDetails();
        } else {
            alert("No company ID provided!");
            window.location.href = "/student_dashboard";
        }
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
        
        async fetchCompanyDetails() {
            try {
                const response = await fetch(`/api/student/company/${this.companyId}`, {
                    headers: this.getHeaders(),
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.studentName = data.studentName;
                    this.company = data.company;
                    this.loading = false;
                } else {
                    alert("Failed to load company details.");
                    window.location.href = "/student_dashboard";
                }
            } catch (error) {
                console.error("Error:", error);
            }
        },
        
        async viewDriveDetails(driveId) {
            window.location.href = `/student_view_drive_details?id=${driveId}`;
        },
    },
}).mount("#app");