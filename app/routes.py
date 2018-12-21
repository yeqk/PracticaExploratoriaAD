import os
import sys

import pytz
from werkzeug.urls import url_parse
from sqlalchemy import desc, or_
from app import app, db, images
from app.forms import LoginForm, RegisterForm, AddAdForm, SearchForm
from app.models import User, Ad, Image
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    print('aaa',file=sys.stdout)
    ads = Ad.query.order_by(desc(Ad.timestamp)).all()
    prices = []
    for ad in ads:
        prices.append(round(ad.price, 2))
    search_form = SearchForm()
    return render_template('home.html', ads=enumerate(ads), title='Home', prices=prices, form = search_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #Si no esta autentificat, es redirigit cap al home
    print('aqui')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        #Si no existeix l'usuari o el password es incorrecte, s'envia a login un altre vegada
        if user is None or not user.check_password(login_form.psw.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        #Login fet
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        #Si no existeix la pagina seguent o la pagina seguent no es un url complet, s'envia cap al home
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form = login_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User(username=register_form.username.data)
        user.set_password(register_form.psw.data)
        db.session.add(user)
        db.session.commit()
        flash('Successfully registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form = register_form)

@app.route('/myaccount')
@login_required
def myaccount():
    return render_template('account.html')

#endpoint per buscar anunci
@app.route('/search', methods=['POST'])
def search():
    ads_result = []
    prices_result = []
    search_form = SearchForm()
    if search_form.validate_on_submit():
        value = search_form.search_field.data
        if search_form.category.data == 'All':
            ads_result = Ad.query.order_by(desc(Ad.timestamp)) \
                .filter((Ad.price >= search_form.price_min.data) & (Ad.price <= search_form.price_max.data)) \
                .filter((Ad.title.like("%" + value + "%")) | (Ad.category.like("%" + value + "%")) | (
                Ad.description.like("%" + value + "%")))
            for ad_result in ads_result:
                prices_result.append(round(ad_result.price, 2))
            return render_template('search.html', title='Search', ads=enumerate(ads_result), prices=prices_result, form=search_form)
        else:
            ads_result = Ad.query.order_by(desc(Ad.timestamp)) \
                .filter(Ad.category == search_form.category.data) \
                .filter((Ad.price >= search_form.price_min.data) & (Ad.price <= search_form.price_max.data)) \
                .filter((Ad.title.like("%" + value + "%")) | (Ad.category.like("%" + value + "%")) | (
                Ad.description.like("%" + value + "%")))
            for ad_result in ads_result:
                prices_result.append(round(ad_result.price, 2))
            return render_template('search.html', title='Search', ads=enumerate(ads_result), prices=prices_result,
                                   form=search_form)
    return render_template('search.html',title='Search',ads=enumerate(ads_result),form=search_form )
#endpoint per afegir un anunci
@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    add_form = AddAdForm()
    if add_form.validate_on_submit():
        u = User.query.get(int(current_user.get_id()))
        date_time = datetime.now(pytz.timezone("Europe/Madrid"))
        ad = Ad(title=add_form.title.data, description=add_form.description.data, category=add_form.category.data, price=add_form.price.data, timestamp=date_time,author=u)
        db.session.add(ad)
        for data in add_form.images.data:
            if not isinstance(data, str):
                filename = images.save(data, folder=current_user.username)
                url = images.url(filename)
                img = Image(image_filename=filename, image_url=url, from_ad=ad)
                db.session.add(img)
        db.session.commit()
        flash('Successfully added!')
        return redirect(url_for('myaccount'))
    return render_template('add_ad.html', title='Add Advertisement', form=add_form)

#endpoint per gestionar els anunics del propi usuari
@app.route('/myads')
@login_required
def myads():
    ads = Ad.query.order_by(desc(Ad.timestamp)) \
    .filter(Ad.user_id == int(current_user.get_id()))
    prices = []
    for ad in ads:
        prices.append(round(ad.price, 2))
    return render_template('myads.html', ads=enumerate(ads), title='My Ads', prices=prices)

#endpoint per mostrar les imatges
@app.route('/view', methods = ['POST', 'GET'])
def view_imgs():
    if request.method == 'POST':
        ad_id = request.form['id']
        imgs = Ad.query.get(int(ad_id)).images.all()
        return render_template('image_viewer.html', title = 'Image Viewer',images = imgs, edit = False, ad_id = ad_id)
    return redirect(url_for('home'))


@app.route('/remove_imgs', methods = ['POST'])
@login_required
def remove_imgs():
    if request.method == 'POST':
        ad_id = request.form['id']
        imgs = Ad.query.get(int(ad_id)).images.all()
        for img in imgs:
            os.remove(os.path.join(app.config['UPLOADED_IMAGE_DEST'], 'images'+ '\\' + img.image_filename.replace("/","\\")))
            db.session.delete(img)
        db.session.commit()
        flash('Images removed!')
    ads = Ad.query.order_by(desc(Ad.timestamp)) \
        .filter(Ad.user_id == int(current_user.get_id()))
    prices = []
    for ad in ads:
        prices.append(round(ad.price, 2))
    return render_template('myads.html', ads=enumerate(ads), title='My Ads', prices=prices)

#remove img
@app.route('/remove_img', methods = ['POST'])
@login_required
def remove_img():
    if request.method == 'POST':
        img_id = request.form['img_id']
        print('aqui')
        img = Image.query.get(int(img_id))
        print('a2')
        os.remove(os.path.join(app.config['UPLOADED_IMAGE_DEST'], 'images' + '\\' + img.image_filename.replace("/", "\\")))
        db.session.delete(img)
        db.session.commit()
        print('a4')
        ad_id = request.form['adv_id']
        print('a3')
        imgs = Ad.query.get(int(ad_id)).images.all()
        print('aqui2')
        return render_template('image_viewer.html', title='Image Viewer', images=imgs, edit=True, ad_id = ad_id)
    return redirect(url_for('myads'))


@app.route('/edit_imgs', methods = ['POST'])
@login_required
def edit_imgs():
    if request.method == 'POST':
        ad_id = request.form['id']
        imgs = Ad.query.get(int(ad_id)).images.all()
        return render_template('image_viewer.html', title='Edit Images', images = imgs, edit = True, ad_id = ad_id)
    return redirect(url_for('myads'))

@app.route('/edit_ad', methods = ['POST'])
@login_required
def edit_ad():
    print("request ====", request)
    if request.method == 'POST':
        ad_id = request.form['id']
        add_form = AddAdForm()
        ad = Ad.query.get(int(ad_id))
        add_form.title.data = ad.title
        add_form.category.data = ad.category
        add_form.price.data = round(ad.price, 2)
        add_form.description.data = ad.description
        return render_template('edit_ad.html', title='Edit Advertisement', form=add_form, id=ad_id)
    return redirect(url_for('myads'))

@app.route('/save_edit', methods = ['POST'])
@login_required
def save_edit():
    if request.method == 'POST':
        ad_id = request.form['id']
        add_form = AddAdForm()
        ad = Ad.query.get(int(ad_id))
        ad.title = add_form.title.data
        ad.category = add_form.category.data
        ad.description = add_form.description.data
        ad.price = add_form.price.data
        ad.timestamp = datetime.now(pytz.timezone("Europe/Madrid"))
        for data in add_form.images.data:
            if not isinstance(data, str):
                filename = images.save(data, folder=current_user.username)
                url = images.url(filename)
                img = Image(image_filename=filename, image_url=url, from_ad=ad)
                db.session.add(img)
        db.session.commit()
        flash('Ad editted!')
    return redirect(url_for('myads'))


@app.route('/remove_ad', methods = ['POST'])
@login_required
def remove_ad():
    if request.method == 'POST':
        ad_id = request.form['id']
        imgs = Ad.query.get(int(ad_id)).images.all()
        for img in imgs:
            os.remove(os.path.join(app.config['UPLOADED_IMAGE_DEST'],'images' + '\\' + img.image_filename.replace("/", "\\")))
            db.session.delete(img)
        ad_to_delete = Ad.query.filter_by(id=int(ad_id)).first()
        db.session.delete(ad_to_delete)
        db.session.commit()
        flash('Ad removed!')
    ads = Ad.query.order_by(desc(Ad.timestamp)) \
        .filter(Ad.user_id == int(current_user.get_id()))
    prices = []
    for ad in ads:
        prices.append(round(ad.price, 2))
    return render_template('myads.html', ads=enumerate(ads), title='My Ads', prices=prices)