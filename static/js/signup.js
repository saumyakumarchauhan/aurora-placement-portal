const { createApp } = Vue;

createApp({
    data() {
        return {
            name: "",
            email: "",
            password: "",
            role: "student",

            department: "",
            cgpa: "",
            year_of_study: "",

            hr_contact: "",
            website: "",
            description: "",

            message: "",
            success: false,
        };
    },
    methods: {
        async handleRegister() {
            this.message = "";
            this.success = false;

            let payload = {
                email: this.email,
                password: this.password,
                role: this.role,
            };

            if (this.role === "student") {
                payload.full_name = this.name;
                payload.department = this.department;
                payload.cgpa = this.cgpa;
                payload.year_of_study = this.year_of_study;
            } else {
                payload.company_name = this.name;
                payload.hr_contact = this.hr_contact;
                payload.website = this.website;
                payload.description = this.description;
            }

            try {
                const response = await fetch("/signup", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(payload),
                });

                const data = await response.json();

                if (response.ok) {
                    this.success = true;
                    this.message = "Registration successful! Redirecting to login...";

                    setTimeout(() => {
                        window.location.href = "/login";
                    }, 2000);
                } else {
                    this.success = false;
                    this.message = data.error || "Registration failed";
                }
            } catch (error) {
                this.success = false;
                this.message = "Server error. Please try again.";
            }
        },
    },
}).mount("#signupApp");