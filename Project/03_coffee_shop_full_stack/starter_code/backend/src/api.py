import os
from flask import Flask, request, jsonify, flash, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def get_drinks():

    try:
        data=[{
            "name": "water",
            "color": "blue",
            "parts": 1
        }]
        # data.append({(drink.short())for drink in Drink.query.all()})
        if len(data)==0:
            return jsonify({
                "success": True,
                "drinks": "None available at the moment"
            }), 200
        else:
            return jsonify(
                {
                    "success": True,
                    "drinks": data
                }
            ), 200
    except:
        abort(400)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):

    try:
        data=[]
        data.append({drink.long()for drink in Drink.querry.all()})
        if len(data)==0:
            return jsonify({
                "success": True,
                "drinks": "No detail available at the moment"
            }), 200
        else:
            return jsonify(
                {
                    "success": True,
                    "drinks": data
                }
            ), 200
    except:
        abort(400)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(payload):
    data=[]
    body = request.get_json()

    title = body.get("title", None)
    recipe = body.get("recipe", None)
    recipe = json.dumps(recipe)

    if title is None or recipe is None:
        abort(404)
    try:
        new_drink = Drink(
            title=title,
            recipe=recipe
        )
        new_drink.insert()
        data.append(new_drink.long())

        return jsonify(
            {
                "success": True,
                "drinks": data
            }
        ), 200

    except:
        db.session.rollback()
        flash(f"{new_drink} drink not created")
        abort(422)

    finally:
        db.session.close()


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, drink_id):
    data=[]
    body = request.get_json()
    title = body.get("title", None)
    recipe = body.get("recipe", None)
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        if title is not None:
            drink.title = title

        if recipe is not None:
            drink.recipe = json.dumps(body["recipe"])

        drink.update()
        data.append(drink.long())

        return jsonify(
            {
                "success": True,
                "drinks": data,
            }
        ), 200

    except:
        db.session.rollback()
        flash(f"{drink} drink could not be updated")
        abort(422)

    finally:
        db.session.close()


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(payload, drink_id):
    data=[]
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        data.append(drink.long())
        drink.delete()
        return jsonify(
            {
                "success": True,
                "delete": data
            }
        ), 200

    except Exception:
        db.session.rollback()
        flash(f"An error occured, {drink} drink could not be deleted")
        abort(422)

    finally:
        db.session.close()


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify(
        {
            "success": False,
            "error": 400,
            "message": "bad request"
        }
    ), 400

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            "success": False,
            "error": 404,
            "message": "resource not found"
        }
    ), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_error(auth_error):
    return jsonify(
        {
            "success": False,
            "error": auth_error.status_code,
            "message": auth_error.error['description']
        }
    ), auth_error.status_code
