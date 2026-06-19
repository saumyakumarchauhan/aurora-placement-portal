const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: true,
            driveId: null,
            studentName: "Loading...",
            applied: false,
            resumeUrl: "", // <--- Add this new variable
            drive: {},
        };
    },
    mounted() {
        const urlParams = new URLSearchParams(window.location.search);
        this.driveId = urlParams.get("id");
        if (this.driveId) {
            this.fetchDriveDetails();
        } else {
            alert("No drive ID provided!");
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

        async fetchDriveDetails() {
            try {
                const response = await fetch(`/api/student/drive/${this.driveId}`, {
                    headers: this.getHeaders(),
                });
                if (response.ok) {
                    const data = await response.json();
                    this.drive = data;
                    this.applied = data.applied;
                    this.loading = false;
                } else {
                    alert("Failed to load drive details.");
                    window.location.href = "/student_dashboard";
                }
            } catch (error) {
                console.error("Error:", error);
            }
        },

        async applyForDrive() {
            // NEW: Validate that they entered a link!
            if (!this.resumeUrl) {
                alert("Please provide a link to your resume before applying!");
                return;
            }

            if (confirm(`Are you sure you want to apply for ${this.drive.jobTitle}?`)) {
                try {
                    const response = await fetch(`/api/student/apply/${this.driveId}`, {
                        method: "POST",
                        headers: this.getHeaders(),
                        // NEW: Send the resume URL to the backend
                        body: JSON.stringify({ resume_url: this.resumeUrl }),
                    });

                    if (response.ok) {
                        this.applied = true;
                    } else {
                        const data = await response.json();
                        alert(data.error || "Failed to submit application.");
                    }
                } catch (error) {
                    alert("Server error. Please try again later.");
                }
            }
        },
    },
}).mount("#app");