const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: true,
            appId: null,
            statusMessage: "",
            student: {},
        };
    },
    mounted() {
        const urlParams = new URLSearchParams(window.location.search);
        this.appId = urlParams.get("id");
        if (this.appId) {
            this.fetchStudentDetails();
        } else {
            alert("No application ID provided!");
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

        async fetchStudentDetails() {
            try {
                const response = await fetch(
                    `/api/company/student_application/${this.appId}`,
                    {
                        headers: this.getHeaders(),
                    }
                );

                if (response.ok) {
                    this.student = await response.json();
                    this.loading = false;
                } else {
                    alert("Failed to load application details.");
                    window.location.href = "/company_dashboard";
                }
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        },

        viewResume() {
            if (this.student.resumeUrl && this.student.resumeUrl !== "#") {
                window.open(this.student.resumeUrl, "_blank");
            } else {
                alert("This student has not uploaded a resume yet.");
            }
        },

        async statusChanged() {
            try {
                // Reuse the existing update_application route from your backend
                const response = await fetch(
                    `/api/company/update_application/${this.appId}`,
                    {
                        method: "POST",
                        headers: this.getHeaders(),
                        body: JSON.stringify({ status: this.student.status }),
                    }
                );

                if (response.ok) {
                    this.statusMessage = "Status successfully updated to: " + this.student.status;
                    setTimeout(() => {
                        this.statusMessage = "";
                    }, 3000);
                } else {
                    alert("Failed to update status.");
                }
            } catch (error) {
                alert("Server error while updating status.");
            }
        },
    },
}).mount("#app");