/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#3B82F6',
                    dark: '#2563EB',
                    light: '#60A5FA',
                },
                secondary: {
                    DEFAULT: '#6B7280',
                    dark: '#4B5563',
                    light: '#D1D5DB',
                },
                background: '#F9FAFB',
                card: '#FFFFFF',
                accent: '#10B981',
                text: '#1F2937',
                success: {
                    DEFAULT: '#10B981',
                    dark: '#059669',
                    light: '#6EE7B7',
                },
                danger: {
                    DEFAULT: '#EF4444',
                    dark: '#DC2626',
                    light: '#FCA5A5',
                },
                warning: {
                    DEFAULT: '#F59E0B',
                    dark: '#D97706',
                    light: '#FDE68A',
                },
            },
            fontFamily: {
                sans: ['Inter', 'ui-sans-serif', 'system-ui'],
            },
            boxShadow: {
                card: '0 4px 12px rgba(0, 0, 0, 0.05)',
                soft: '0 2px 8px rgba(0, 0, 0, 0.03)',
            },
        },
    },
    plugins: [],
}
