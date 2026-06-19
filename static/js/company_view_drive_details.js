const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: true,
            saving: false,
            driveId: null,
            companyName: "Loading...",
            jobTitle: "Loading...",
            driveStatus: "",
            applications: [],
        };
    },
    mounted() {
        const urlParams = new URLSearchParams(window.location.search);
        this.driveId = urlParams.get("id");
        if (this.driveId) {
            this.fetchDriveDetails();
        } else {
            alert("No drive ID provided!");
            window.location.href = "/company_dashboard";
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

        async fetchDriveDetails() {
            try {
                const response = await fetch(`/api/company/drive/${this.driveId}`, {
                    headers: this.getHeaders(),
                });

                if (response.ok) {
                    const data = await response.json();
                    this.companyName = "Company Portal";
                    this.jobTitle = data.jobTitle;
                    this.driveStatus = data.status;
                    this.applications = data.applicants;
                    this.loading = false;
                } else {
                    alert("Failed to load drive details.");
                    window.location.href = "/company_dashboard";
                }
            } catch (error) {
                console.error("Error:", error);
            }
        },

        async saveChanges() {
            this.saving = true;
            try {
                // Loop through applications and update them in the backend
                for (let student of this.applications) {
                    await fetch(`/api/company/update_application/${student.id}`, {
                        method: "POST",
                        headers: this.getHeaders(),
                        body: JSON.stringify({ status: student.status }),
                    });
                }
                alert("Application statuses updated successfully!");
                // Redirect back to the dashboard!
                window.location.href = "/company_dashboard";
            } catch (error) {
                alert("Error saving changes. Please try again.");
            } finally {
                this.saving = false;
            }
        },
    },
}).mount("#app");