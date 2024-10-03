from app import create_app, create_db



app = create_app()

db = create_db(app)

if __name__ =='__main__':
    app.run(port=5001, debug=True)


