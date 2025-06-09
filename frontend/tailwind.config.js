/** @type {import('tailwindcss').Config} */
export default {
	darkMode: ["class"],
	content: [
		'./pages/**/*.{ts,tsx}',
		'./components/**/*.{ts,tsx}',
		'./app/**/*.{ts,tsx}',
		'./src/**/*.{ts,tsx}',
	],
	safelist: [
		// AWS color classes that need to be included
		{
			pattern: /^(bg|text|border|ring|from|to|via|outline|decoration|accent|caret|fill|stroke|shadow|drop-shadow)-(aws-)?(gray|orange|blue)(-light)?-(50|100|200|300|400|500|600|700|800|900)$/,
		},
		{
			pattern: /^(bg|text|border|ring|from|to|via|outline|decoration|accent|caret|fill|stroke|shadow|drop-shadow)-(aws-)?(orange|blue)(-light|-foreground)?$/,
		},
		// Common AWS utility classes
		'bg-aws-orange',
		'bg-aws-blue',
		'bg-aws-blue-light',
		'text-aws-orange',
		'text-aws-blue',
		'text-aws-blue-light',
		'border-aws-orange',
		'border-aws-blue',
		'border-aws-blue-light',
		'hover:bg-aws-orange',
		'hover:bg-aws-blue',
		'hover:text-aws-orange',
		'hover:text-aws-blue',
		'focus:border-aws-blue',
		'focus:ring-aws-blue',
		'data-[state=active]:text-aws-blue',
		'data-[state=active]:text-aws-orange',
		'data-[state=active]:border-aws-blue',
		'data-[state=active]:border-aws-orange',
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px'
			}
		},
		extend: {
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				chart: {
					'1': 'hsl(var(--chart-1))',
					'2': 'hsl(var(--chart-2))',
					'3': 'hsl(var(--chart-3))',
					'4': 'hsl(var(--chart-4))',
					'5': 'hsl(var(--chart-5))'
				},
				// AWS brand colors
				aws: {
					orange: 'hsl(var(--aws-orange))',
					'orange-foreground': 'hsl(var(--aws-orange-foreground))',
					blue: 'hsl(var(--aws-blue))',
					'blue-light': 'hsl(var(--aws-blue-light))',
					gray: {
						50: 'hsl(var(--aws-gray-50))',
						100: 'hsl(var(--aws-gray-100))',
						200: 'hsl(var(--aws-gray-200))',
						300: 'hsl(var(--aws-gray-300))',
						400: 'hsl(var(--aws-gray-400))',
						500: 'hsl(var(--aws-gray-500))',
						600: 'hsl(var(--aws-gray-600))',
						700: 'hsl(var(--aws-gray-700))',
						800: 'hsl(var(--aws-gray-800))',
						900: 'hsl(var(--aws-gray-900))'
					}
				}
			},
			borderRadius: {
				lg: 'var(--radius)', // Should be 0.25rem based on :root
				md: 'calc(var(--radius) - 0.05rem)', // Adjusted for smaller base radius
				sm: 'calc(var(--radius) - 0.1rem)' // Adjusted for smaller base radius
			},
			keyframes: {
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out'
			}
		}
	},
	plugins: [require("tailwindcss-animate")],
}
