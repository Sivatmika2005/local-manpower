import os

directory = r"d:\Projects\FSD\localservicebookingnew\backend_django\core\templates\core"
replacements = {
    'window.location.href = "/admin_dashboard.html"': 'window.location.href = "{% url \'admin_dashboard\' %}"',
    'window.location.href = "/provider_dashboard.html"': 'window.location.href = "{% url \'provider_dashboard\' %}"',
    'window.location.href = "home.html"': 'window.location.href = "{% url \'home\' %}"',
    'location.href = "login.html"': 'location.href = "{% url \'login\' %}"',
    'location.href = "home.html"': 'location.href = "{% url \'home\' %}"',
}
for filename in os.listdir(directory):
    if filename.endswith(".html"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for old, new in replacements.items():
            new_content = new_content.replace(old, new)
            
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
