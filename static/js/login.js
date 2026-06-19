const { createApp } = Vue;

createApp({
    data() {
        return {
            email: "",
            password: "",
            error: "",
            loading: false,
        };
    },
    methods: {
        async handleLogin() {
            this.error = "";
            this.loading = true;

            try {
                const response = await fetch("http://127.0.0.1:5000/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        email: this.email,
                        password: this.password,
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    this.error = data.error || "Login failed";
                    this.loading = false;
                    return;
                }

                // Save token
                localStorage.setItem("access_token", data.access_token);
                localStorage.setItem("role", data.role);

                // Redirect based on role
                if (data.role === "admin") {
                    window.location.href = "/admin_dashboard";
                } else if (data.role === "student") {
                    window.location.href = "/student_dashboard";
                } else if (data.role === "company") {
                    window.location.href = "/company_dashboard";
                }
            } catch (err) {
                this.error = "Server not reachable. Please check your connection.";
            } finally {
                this.loading = false;
            }
        },
    },
}).mount("#loginApp");