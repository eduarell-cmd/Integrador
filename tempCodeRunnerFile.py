@app.route('/logout')
def logout():
    ID_Persona = session.get('user_id')
    if not ID_Persona:
        print("Aqui falla /logout")
        return redirect(url_for('login'))
    user = get_user_by_email(ID_Persona)
    email = user['email'] if user else None
    session.pop('user_id', None)
    session.clear()
    flash("Has cerrado sesión exitosamente", "info")
    return redirect(url_for('index'))     
