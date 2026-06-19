const { createApp } = Vue;

createApp({
  data() {
    return {
      loading: true,
      appId: null,
      application: {},
    };
  },
  mounted() {
    const urlParams = new URLSearchParams(window.location.search);
    this.appId = urlParams.get("id");
    if (this.appId) {
      this.fetchApplicationDetails();
    } else {
      alert("No application ID provided!");
      window.location.href = "/admin_dashboard";
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
    async fetchApplicationDetails() {
      try {
        const response = await fetch(
          `/api/admin/student_application/${this.appId}`,
          {
            headers: this.getHeaders(),
          },
        );

        if (response.ok) {
          this.application = await response.json();
          this.loading = false;
        } else {
          alert("Failed to load application details.");
          window.location.href = "/admin_dashboard";
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },
    viewResume() {
      if (this.application.resumeUrl && this.application.resumeUrl !== "#") {
        window.open(this.application.resumeUrl, "_blank");
      } else {
        alert("This student has not uploaded a resume yet.");
      }
    },
  },
}).mount("#app");
