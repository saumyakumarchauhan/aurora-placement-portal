const { createApp } = Vue;

createApp({
    data() {
        return {
            profile: { name: "", cgpa: "", branch: "", resume_path: "" },
            selectedFile: null,
            isLoading: false,
            alertMsg: "",
            alertType: "success",
        };
    },
    mounted() {
        this.fetchProfile();
    },
    methods: {
        getHeaders() {
            return {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            };
        },

        async fetchProfile() {
            try {
                const res = await fetch("/api/student/profile", {
                    headers: { ...this.getHeaders(), "Content-Type": "application/json" },
                });
                if (res.ok) {
                    this.profile = await res.json();
                }
            } catch (e) {
                console.error("Error fetching profile");
            }
        },

        handleFileUpload(event) {
            this.selectedFile = event.target.files[0];
        },

        async updateProfile() {
            this.isLoading = true;
            this.alertMsg = "";

            // Form Data banana padega kyunki File upload JSON se nahi hota
            const formData = new FormData();
            formData.append("name", this.profile.name);
            formData.append("cgpa", this.profile.cgpa);
            if (this.profile.branch) formData.append("branch", this.profile.branch);

            // Agar nayi file select ki hai toh usko bhi bhejo
            if (this.selectedFile) {
                formData.append("resume", this.selectedFile);
            }

            try {
                const response = await fetch("/api/student/profile", {
                    method: "POST",
                    headers: this.getHeaders(), // Yahan Content-Type set mat karna, browser apne aap multipart form-data lega
                    body: formData,
                });

                const data = await response.json();
                if (response.ok) {
                    this.alertType = "success";
                    this.alertMsg = data.message;
                    this.fetchProfile(); // Data reload karne ke liye
                } else {
                    this.alertType = "danger";
                    this.alertMsg = "Failed to update profile.";
                }
            } catch (error) {
                this.alertType = "danger";
                this.alertMsg = "Server error occurred.";
            } finally {
                this.isLoading = false;
            }
        },
    },
}).mount("#app");