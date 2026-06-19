const { createApp } = Vue;

createApp({
    data() {
        return {
            companyName: "Loading...",
            upcomingDrives: [],
            closedDrives: [],
        };
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
                const response = await fetch("/api/company/data", {
                    method: "GET",
                    headers: this.getHeaders(),
                });

                if (response.status === 401 || response.status === 403) {
                    window.location.href = "/login";
                    return;
                }

                const data = await response.json();
                if (response.ok) {
                    this.companyName = data.companyName;
                    this.upcomingDrives = data.upcomingDrives;
                    this.closedDrives = data.closedDrives;
                }
            } catch (error) {
                console.error("Error fetching company data:", error);
            }
        },

        createDrive() {
            window.location.href = "/company_create_drive";
        },

        viewDetails(driveId) {
            window.location.href = `/company_view_drive_details?id=${driveId}`;
        },

        updateDrive(driveId) {
            window.location.href = `/company_view_drive_details?id=${driveId}`;
        },

        async markComplete(drive) {
            if (confirm(`Are you sure you want to mark '${drive.name}' as complete? This will move it to Closed Drives.`)) {
                try {
                    const response = await fetch(`/api/company/mark_complete/${drive.id}`, {
                        method: "POST",
                        headers: this.getHeaders(),
                    });

                    if (response.ok) {
                        this.fetchDashboardData();
                    } else {
                        alert("Failed to close drive.");
                    }
                } catch (error) {
                    alert("Server error.");
                }
            }
        },
    },
}).mount("#app");