from blog import app
import blog.views

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'])
