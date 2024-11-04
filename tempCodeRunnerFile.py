@app.route(f'/{admin_key}')
def admin_dashboard():
     return render_template('admin.html')
