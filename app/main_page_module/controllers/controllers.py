import json

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify, send_file, Response, abort

# Import module forms
from app.main_page_module.forms import form_dicts
#from app.main_page_module.p_objects.note_o import N_obj


from wrappers import login_required, online_required
from app.pylavor import Pylavor
from app.main_page_module.other import Randoms
from app.main_page_module.gears import Gears_obj
from app.main_page_module.p_objects.artifact import Artifact
from app.main_page_module.p_objects.excel_artifaks import ExcelO


from app import app

#import os
import re
import os
import zipfile
import io
import pathlib
from passlib.hash import sha512_crypt
import datetime


# Define the blueprint: 'auth', set its url prefix: app.url/auth
main_page_module = Blueprint('main_page_module', __name__, url_prefix='/')


@app.context_processor
def inject_to_every_page():
    
    return dict(Randoms=Randoms, datetime=datetime, Pylavor=Pylavor, Artifact=Artifact)


@main_page_module.route('/', methods=['GET'])
def offline():
    return render_template("main_page_module/offline.html")

@main_page_module.route('/index', methods=['GET'])
@online_required(app.config['ONLINE'])
def index():
    return render_template("main_page_module/index.html")

@main_page_module.route('/artifacts/<type_>', methods=['GET'])
@main_page_module.route('/artifacts/', methods=['GET'])
@online_required(app.config['ONLINE'])
def artifacts(type_="all"):    
    return render_template("main_page_module/artifacts/artifacts_all.html",
                           type_=type_)

@main_page_module.route('/artifacts_new/', methods=['GET', 'POST'])
@online_required(app.config['ONLINE'])
@login_required
def artifacts_new():
    form = form_dicts["Artifact"]()

    if form.validate_on_submit():
        col_ref_num = Artifact.col_ref_num_new(form.type_.data)
        
        art_data = {"col_ref_num": col_ref_num,
            "name": form.name.data,
            "type_": form.type_.data,
            "period": form.period.data,
            "state_entity": form.state_entity.data,
            "replica": form.replica.data,
            "provenance_notes": form.provenance_notes.data,
            "owners": form.owners.data,
            "description": form.description.data,
            "historical_context": form.historical_context.data,
            "buy_price": form.buy_price.data,
            "sold_price": form.sold_price.data,
            "joined_collection_in_year": form.joined_collection_in_year.data,
            "left_collection_in_year": form.left_collection_in_year.data,
            "reference": form.reference.data,
            "public": form.public.data,
            "curr_location_of_item": form.curr_location_of_item.data,
            "coin_type": form.coin_type.data,
            "coin_description": form.coin_description.data,
            "ruler": form.ruler.data,
            "mint_city": form.mint_city.data,
            "mint_period": form.mint_period.data,
            "material": form.material.data,
            "weight": form.weight.data,
            "diameter": form.diameter.data,
            "obverse": form.obverse.data,
            "reverse": form.reverse.data,
            "grade": form.grade.data
            }

        artifact = Artifact(art_data)
        
        try:
            artifact.save()
            flash('Artifakt uspešno shranjen!', 'success')
            return redirect(url_for("main_page_module.artifacts_view", col_ref_num=col_ref_num))
            
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju artifakta!', 'error')        
        
    
    for error in form.errors:
        print(error)
        flash(f'Invalid Data: {error}', 'error')    

    return render_template("main_page_module/artifacts/artifacts_new.html", form=form)



@main_page_module.route('/artifacts_view/<col_ref_num>', methods=['GET'])
@online_required(app.config['ONLINE'])
def artifacts_view(col_ref_num):
    art_data = Artifact.get_one(col_ref_num)
    
    if art_data is False or (('user_id' not in session) and (art_data["public"] != "1")):
        flash(f'Artifakt ne obstaja.', 'error')
        return redirect(url_for('main_page_module.artifacts'))            
    
    artifact = Artifact(art_data)
    
    return render_template("main_page_module/artifacts/artifacts_view.html", artifact=artifact)


@main_page_module.route('/artifacts_edit/', methods=['POST'])
@main_page_module.route('/artifacts_edit/<col_ref_num>', methods=['GET', 'POST'])
@login_required
@online_required(app.config['ONLINE'])
def artifacts_edit(col_ref_num:str=None):
    form = form_dicts["Artifact"]()
    
    if col_ref_num == None:
        col_ref_num = form.col_ref_num.data
    else:
        form.col_ref_num.data = col_ref_num
    
    art_data = Artifact.get_one(col_ref_num)
    
    if art_data is False:
        flash(f'Artifakt ne obstaja.', 'error')
        return redirect(url_for('main_page_module.artifacts'))

    artifact = Artifact(art_data)

    # GET
    if request.method == 'GET':
        form.process(col_ref_num = art_data["col_ref_num"],
                     name = art_data["name"],
                     type_ = art_data["type_"],
                     period = art_data["period"],
                     state_entity = art_data["state_entity"],
                     replica = art_data["replica"],
                     provenance_notes = art_data["provenance_notes"],
                     owners = art_data["owners"],
                     description = art_data["description"],
                     historical_context = art_data["historical_context"],
                     buy_price = art_data["buy_price"],
                     sold_price = art_data["sold_price"],
                     joined_collection_in_year = art_data["joined_collection_in_year"],
                     left_collection_in_year = art_data["left_collection_in_year"],
                     reference = art_data["reference"],
                     public = art_data["public"],
                     curr_location_of_item = art_data["curr_location_of_item"],
                     coin_type = art_data["coin_type"],
                     coin_description = art_data["coin_description"],
                     ruler = art_data["ruler"],
                     mint_city = art_data["mint_city"],
                     mint_period = art_data["mint_period"],
                     material = art_data["material"],
                     weight = art_data["weight"],
                     diameter = art_data["diameter"],
                     obverse = art_data["obverse"],
                     reverse = art_data["reverse"],
                     grade = art_data["grade"])
    
    # POST
    if form.validate_on_submit():
        art_data = {"col_ref_num": col_ref_num,
            "name": form.name.data,
            "type_": form.type_.data,
            "period": form.period.data,
            "state_entity": form.state_entity.data,
            "replica": form.replica.data,
            "provenance_notes": form.provenance_notes.data,
            "owners": form.owners.data,
            "description": form.description.data,
            "historical_context": form.historical_context.data,
            "buy_price": form.buy_price.data,
            "sold_price": form.sold_price.data,
            "joined_collection_in_year": form.joined_collection_in_year.data,
            "left_collection_in_year": form.left_collection_in_year.data,
            "reference": form.reference.data,
            "public": form.public.data,
            "curr_location_of_item": form.curr_location_of_item.data,
            "coin_type": form.coin_type.data,
            "coin_description": form.coin_description.data,
            "ruler": form.ruler.data,
            "mint_city": form.mint_city.data,
            "mint_period": form.mint_period.data,
            "material": form.material.data,
            "weight": form.weight.data,
            "diameter": form.diameter.data,
            "obverse": form.obverse.data,
            "reverse": form.reverse.data,
            "grade": form.grade.data
            }
        
        artifact = Artifact(art_data)

        try:
            artifact.save()
            
            if form.image.data != None:
                file_ = form.image.data
                artifact.write_image(file_)            
            
            flash('Artifakt uspešno shranjen!', 'success')
            return redirect(url_for("main_page_module.artifacts_view", col_ref_num=col_ref_num, artifact=artifact))
            
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju artifakta!', 'error')
        
    
    for field, errors in form.errors.items():
        print(f'Field: {field}')
        for error in errors:
            flash(f'Invalid Data for {field}: {error}', 'error')
    
    
    return render_template("main_page_module/artifacts/artifacts_edit.html", form=form, artifact=artifact)


@main_page_module.route('/artifacts_delete_image/<col_ref_num>/<image_name>', methods=['GET'])
@online_required(app.config['ONLINE'])
@login_required
def artifacts_delete_image(col_ref_num, image_name):
    art_data = Artifact.get_one(col_ref_num)
    
    if art_data is False or (('user_id' not in session) and (art_data["public"] != "1")):
        flash(f'Artifakt ne obstaja.', 'error')
        return redirect(url_for('main_page_module.artifacts'))            
    
    artifact = Artifact(art_data)
    
    artifact.delete_image(image_name)
    
    flash(f'Slika izbrisana.', 'success')
    
    return render_template("main_page_module/artifacts/artifacts_view.html", artifact=artifact)


# Set the route and accepted methods
@main_page_module.route('/export_artifacts/', methods=['GET'])
@login_required
def export_artifacts():
    try:
        artifacts = Artifact.get_all("all")
    except Exception as e:
        app.logger.warn(f"{e}")
        error_msg = "Napaka pri nalaganju naslovnikov iz datoteke."
        flash(error_msg, 'error')
        
        return redirect(url_for("main_page_module.artifacts"))

    return ExcelO.export_artifacts(artifacts)



# Set the route and accepted methods
@main_page_module.route('/about/', methods=['GET'])
def about():
    return render_template("main_page_module/about.html")

# Set the route and accepted methods
@main_page_module.route('/login/', methods=['GET', 'POST'])
def login():
    if ('user_id' in session):
        return redirect(url_for("main_page_module.index"))
    
    # If sign in form is submitted
    form = form_dicts["Login"]()

    # Verify the sign in form
    if form.validate_on_submit():
        admin_username = app.config['ADMIN_USERNAME']
        admin_password = app.config['ADMIN_PASS_HASH']
        
        # Generate the password hash
        same_pass = sha512_crypt.verify(form.password.data, admin_password)

        if not same_pass or admin_username != form.username_or_email.data:
            error_msg = "Login napačen."
            flash(error_msg, 'error')
            
        else:
            session['user_id'] = 1
            
            #set permanent login, if selected
            if form.remember.data == True:
                session.permanent = True
    
            error_msg = "Dobrodošel!"
            flash(error_msg, 'success')
            
            return redirect(url_for('main_page_module.index'))
    
        

    for field, errors in form.errors.items():
        app.logger.warn(f"Field: {field}")      
        for error in errors:
            flash(f'Invalid Data for {field}: {error}', 'error')

    return render_template("main_page_module/auth/login.html", form=form)
        

@main_page_module.route('/logout/')
def logout():
    #session.pop("user_id", None)
    #session.permanent = False
    session.clear()
    flash('You have been logged out. Have a nice day!', 'success')

    return redirect(url_for("main_page_module.index"))