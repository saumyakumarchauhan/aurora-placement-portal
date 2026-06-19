const { createApp } = Vue;

createApp({
  data() {
    return {
      loading: true,
      driveId: null,
      drive: {},
    };
  },
  mounted() {
    // Get the ID from the URL (e.g., ?id=5)
    const urlParams = new URLSearchParams(window.location.search);
    this.driveId = urlParams.get("id");

    if (this.driveId) {
      this.fetchDriveDetails();
    } else {
      alert("No drive ID provided!");
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

    async fetchDriveDetails() {
      try {
        const response = await fetch(`/api/admin/drive/${this.driveId}`, {
          headers: this.getHeaders(),
        });

        if (response.ok) {
          this.drive = await response.json();
          this.loading = false;
        } else {
          alert("Failed to load drive details.");
          window.location.href = "/admin_dashboard";
        }
      } catch (error) {
        console.error("Error:", error);
      }
    },

    async cancelDrive() {
      if (
        confirm(
          "Are you sure you want to cancel this drive? This action cannot be undone.",
        )
      ) {
        try {
          const response = await fetch(
            `/api/admin/cancel_drive/${this.driveId}`,
            {
              method: "POST",
              headers: this.getHeaders(),
            },
          );

          if (response.ok) {
            alert("Drive successfully cancelled.");
            window.location.href = "/admin_dashboard";
          }
        } catch (e) {
          alert("Error cancelling drive.");
        }
      }
    },
  },
}).mount("#app");
