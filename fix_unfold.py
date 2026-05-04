import re

with open('templates/admin/index.html', 'r') as f:
    content = f.read()

# Replace specific background and border classes to use Unfold's "base" theme colors
content = content.replace('bg-white dark:bg-gray-800', 'bg-white dark:bg-base-900')
content = content.replace('border-gray-100 dark:border-gray-700', 'border-base-200 dark:border-base-800')

content = content.replace('dark:bg-gray-800', 'dark:bg-base-900')
content = content.replace('bg-gray-800', 'bg-base-900')
content = content.replace('bg-gray-50', 'bg-base-50')
content = content.replace('bg-gray-100', 'bg-base-100')
content = content.replace('bg-gray-900', 'bg-base-900')
content = content.replace('dark:bg-gray-900', 'dark:bg-base-900')

content = content.replace('border-gray-50', 'border-base-50')
content = content.replace('border-gray-100', 'border-base-100')
content = content.replace('border-gray-200', 'border-base-200')
content = content.replace('border-gray-600', 'border-base-600')
content = content.replace('border-gray-700', 'border-base-700')

content = content.replace('text-gray-100', 'text-white')
content = content.replace('text-gray-200', 'text-base-200')
content = content.replace('text-gray-300', 'text-base-300')
content = content.replace('text-gray-400', 'text-base-400')
content = content.replace('text-gray-500', 'text-base-500')
content = content.replace('text-gray-700', 'text-base-700')
content = content.replace('text-gray-800', 'text-base-800')

with open('templates/admin/index.html', 'w') as f:
    f.write(content)
