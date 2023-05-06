# Get User. User with id 2 is Admin
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog GET http://127.0.0.1:5000/api/v1/users/2
# User Posts
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog GET http://127.0.0.1:5000/api/v1/users/2/posts/
# User followed posts
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog GET http://127.0.0.1:5000/api/v1/users/2/timeline/

# Get comments
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog GET http://127.0.0.1:5000/api/v1/comments/
# Get a comment
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog GET http://127.0.0.1:5000/api/v1/comments/1

# Get posts
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog GET http://127.0.0.1:5000/api/v1/posts/
# Get a post
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog GET http://127.0.0.1:5000/api/v1/posts/1
# Get post comments
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog GET http://127.0.0.1:5000/api/v1/posts/4/comments/
# Create new post
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog POST \
 http://127.0.0.1:5000/api/v1/posts/ \
 "body=Hello world from *command line*."
# Edit post
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog PUT \
 http://127.0.0.1:5000/api/v1/posts/106 \
 "body=Hello world from *command line*. Edited from command line"

# Add new comment
http --json --auth daniel.ibarrola.sanchez@gmail.com:dog POST \
 http://127.0.0.1:5000/api/v1/posts/106/comments/ \
 "body=Commenting from *command line*."