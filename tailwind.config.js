/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./site/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        product: "#FBEEED",
        background: "#FEFAFA",
        sectionTitle: "#AA3F2F",
        buttonPrimary: "#e55843",
      },
    },
  },
  plugins: [],
};
