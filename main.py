#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
import re
import cgi

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str (self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render (self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    postDate = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):

    def render_addPage(self, title = "", body = "", error = ""):
        blogPost = db.GqlQuery("SELECT * FROM Blog ORDER BY postDate DESC")
        self.render("newpost.html", title = title, body = body, error = error, blogPost = blogPost)

    def get(self):
        self.render_addPage()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Blog(title = title, body = body)
            a.put()
            id = a.key().id()

            self.redirect("/newpost")
        else:
            error = "Please submit both a title and a post!"
            self.render_addPage(title, body, error)

class NewPost(Handler):
    def render_page(self, title = "", body = "", error = ""):
        blogPost = db.GqlQuery("SELECT * FROM Blog ORDER BY postDate DESC LIMIT 5")
        self.render("MainBlog.html", title = title, body = body, error = error, blogPost = blogPost)

    def get(self):
        self.render_page()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = blogPost(title = title, body = body, error = error)
            post.put()
            id = post.key().id()
            self.redirect("/newpost/%s" %d)
        else:
            error = "Please submit both title and body"
            self.render_page(title, body, error)

class ViewPostHandler(Handler):
    def get (self, id):

        #blog_id = blogPost.key().id()
        #title = self.request.get("title")
        #body = self.request.get("body")

        #user_id = user.key().id()
        #blogPost = db.GqlQuery("SELECT * FROM Blog")
        post = Blog.get_by_id(int(id))
        if post:
            t = jinja_env.get_template("viewpost.html")
            response = t.render(post = post)
        else:
            error = "There is not a post with id %s" % id
            t = jinja_env.get_template("404.html")
            response = t.render(error = error)
        #self.write(post.title)
        self.response.out.write(response)

        #rating = self.request.get("rating")
        #movie_id = self.request.get("movie")

        # retreive the movie entity whose id is movie_id
        #movie = Movie.get_by_id(int(movie_id))








app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/newpost/<id:\d+>', ViewPostHandler)
], debug=True)
