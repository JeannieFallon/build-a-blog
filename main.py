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

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Archive(db.Model):
    title = db.StringProperty(required=True)
    blog_post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Index(Handler):
    def get(self):
        self.render("index.html")


class MainPage(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Archive ORDER BY created DESC LIMIT 5")
        self.render("main_blog.html", posts = posts)

    #def render(self, *a, **kw):
        #self._render_text = self.content.replace('\n','<br>')
        #return render_str("main_blog.html", p = self)


class NewPost(Handler):
    def get(self):
        self.render("new_post.html")

    def post(self):
        title = self.request.get("title")
        blog_post = self.request.get("blog_post")

        if title and blog_post:
            new_post = Archive(title=title,blog_post=blog_post)
            new_post_key = new_post.put()
            new_post_id = new_post_key.id()
            self.redirect('/blog/%d' % new_post_id)
        else:
            error = "Please enter both title and content for your post."
            self.render("new_post.html",title=title,blog_post=blog_post,error=error)


class ViewPostHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def get(self, id):
        aPost_id = int(id)
        aPost = Archive.get_by_id (aPost_id, parent=None)
        # aPost = "This is a test string." <<<This test works
        self.render("single_post.html",aPost=aPost)



app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>',ViewPostHandler)
], debug=True)
