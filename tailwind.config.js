/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./site/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        product: "#FBEEED",
        background: "#f3eded",
        sectionTitle: "#c23d20",
        buttonPrimary: "#e55843",
      },
    },
  },
  plugins: [],
};
