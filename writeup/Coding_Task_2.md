# Coding Task 2

## 1. Hardcoded Password

We need to ensure that there are no hardcoded passwords in the source.
To do this, we are going to use python's `os` library , the `python-dotenv` package added to the `requirements.txt` file and code, and store the password in the `.env` file.
This `.env` file will never be uploaded to the git repo, as it will be included in the `.gitignore` file.

The `.env` file will contain the following lines:
```shell
INCUBATOR_AUTH_SECRET=!Q#E%T&U8i6y4r2w
```

### SampleNetworkClient.py

There are two places where the "password" is hardcoded in SampleNetwork Client, `updateInfTemp` and `updateIncTemp`.

The original code:

```python
    def updateInfTemp(self, p, tok) :
        self.updateTime()
        if self.infToken is None : #not yet authenticated
            self.infToken = self.authenticate(self.infPort, b"!Q#E%T&U8i6y4r2w")
        self.infTemps.append(self.getTemperatureFromPort(p, tok)-273)
        #self.infTemps.append(self.infTemps[-1] + 1)
        self.infTemps = self.infTemps[-30:]
        self.infLn.set_data(range(30), self.infTemps)
        return self.infLn,

    def updateIncTemp(self, p, tok) :
        self.updateTime()
        if self.incToken is None : #not yet authenticated
            self.incToken = self.authenticate(self.incPort, b"!Q#E%T&U8i6y4r2w")

        self.incTemps.append(self.getTemperatureFromPort(p, tok)-273)
        #self.incTemps.append(self.incTemps[-1] + 1)
        self.incTemps = self.incTemps[-30:]
        self.incLn.set_data(range(30), self.incTemps)
        return self.incLn,
```

The first thing we need to do is load the os library, and the new dotenv package and library.

```python
import os
from dotenv import load_dotenv

load_dotenv()
```

We need to put the password we want to use into our `.env` file.
```shell
FLASK_APP=app.py
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
FLASK_DEBUG=1 # This is for development.  Remove in Production. 

INCUBATOR_AUTH_SECRET=!Q#E%T&U8i6y4r2w
```

Note, we should use a new password in production, since this password has been burned by being submitted to github.

And then we have to add the call to get the secret key from the .env file
```python
class SimpleNetworkClient :
    def __init__(self, port1, port2) :
        #--- Code snipped for brevity ---#
        
        # Load secret key from environment variable
        self.auth_secret = os.environ.get("INCUBATOR_AUTH_SECRET")
        if not self.auth_secret:
            raise ValueError(
                "Authentication Error"
        )
        #--- Code snipped for brevity ---#
```


Updates to the functions:

```python
    def updateInfTemp(self, p, tok) :
        self.updateTime()
        if self.infToken is None : #not yet authenticated
            self.infToken = self.authenticate(self.infPort, self.auth_secret.encode("utf-8"))
        self.infTemps.append(self.getTemperatureFromPort(p, tok)-273)
        #self.infTemps.append(self.infTemps[-1] + 1)
        self.infTemps = self.infTemps[-30:]
        self.infLn.set_data(range(30), self.infTemps)
        return self.infLn,

    def updateIncTemp(self, p, tok) :
        self.updateTime()
        if self.incToken is None : #not yet authenticated
            self.incToken = self.authenticate(self.incPort, self.auth_secret.encode("utf-8"))

        self.incTemps.append(self.getTemperatureFromPort(p, tok)-273)
        #self.incTemps.append(self.incTemps[-1] + 1)
        self.incTemps = self.incTemps[-30:]
        self.incLn.set_data(range(30), self.incTemps)
        return self.incLn,
```

We have now removed the hardcoded "password" from the SampleNetworkClient, and put it instead into our `.env` file.

### SampleNetworkServer.py

We can see from the processCommands() where the passed password is compared. 
We need to update this so the password is no longer hardcoded here.

Original

```python
    def processCommands(self, msg, addr) :
        cmds = msg.split(';')
        for c in cmds :
            cs = c.split(' ')
            if len(cs) == 2 : #should be either AUTH or LOGOUT
                if cs[0] == "AUTH":
                    if cs[1] == "!Q#E%T&U8i6y4r2w" :
                        self.tokens.append(''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))
                        self.serverSocket.sendto(self.tokens[-1].encode("utf-8"), addr)
                        #print (self.tokens[-1])
            #---  Code Snipped --#
```

We are going to use the same trick here, and use `self.auth_secret` to load the authorization password from a .env file. 
We are also going to use `hmac.compare_digest()` to prevent timing attacks. 
If we use a standard string comparison, the interpreter compares the stings character by character, and returns `False` immediately upon finding a character that does not match.
If an attacker compares the time to fail every time, they can figure out how many characters they have gotten correct before it fails.
Using `hmac.compare_digest()` forces a constant-time equality check, which means every byte is compared.
The time spent comparing is the same regardless of failure or success.

Updated Code:

We need to include the `hmac` library at the top of our code:
```python
import hmac
from dotenv import load_dotenv

load_dotenv()
```

```python
    def __init__ (self, source, updatePeriod, port) :
        #---  Code Snipped --#

        # Load secret key from environment variable
        self.auth_secret = os.environ.get("INCUBATOR_AUTH_SECRET")
        if not self.auth_secret:
            raise ValueError(
                "Authentication Error"
        )
        #---  Code Snipped --#
```

And then we can update our code by importing the password and using a constant-time equality check. 
```python
    def processCommands(self, msg, addr) :
        cmds = msg.split(';')
        for c in cmds :
            cs = c.split(' ')
            if len(cs) == 2 : #should be either AUTH or LOGOUT
                if cs[0] == "AUTH":
                    # Replace Hardcoded Password with auth_secret from .env, and use hmac.compare_digest() to prevent timing attack.
                    if hmac.compare_digest(cs[1].encode(), self.auth_secret.encode()) :
                        self.tokens.append(''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))
                        self.serverSocket.sendto(self.tokens[-1].encode("utf-8"), addr)
                        #print (self.tokens[-1])
                    else:
                        self.serverSocket.sendto("Incorrect password".encode("utf-8"), addr)
                elif cs[0] == "LOGOUT":
                    if cs[1] in self.tokens :
                        self.tokens.remove(cs[1])
                else : #unknown command
                    self.serverSocket.sendto(b"Invalid Command\n", addr)
            #---  Code Snipped --#
```

### Summary

We have replaced the places in SampleNetworkServer.py and SampleNetworkClient.py where the password was hardcoded with a variable taken from the `.env` file.
We will use a new password value stored as `INCUBATOR_AUTH_SECRET` in further versions or in production.
Additionally, we have replaced the string compare with `hmac.compare_digest()` to ensure our app is not vulnerable to a timing attack.


## 2. Token List has potential to continuously grow

In the SampleNetworkServer.py file, an empty token list is created, later on in the code, tokens are appended to this list.
There is no limitation at this point to stop this list from growing indefinitely. 
This can lead to a situation where too many resources are required to keep this information, therefore we are going to limit this list, in order to prevent this type of vulnerability.

### SampleNetworkServer.py

Original Code:

```python
def __init__ (self, source, updatePeriod, port) :
    threading.Thread.__init__(self, daemon = True) 
    #set daemon to be true, so it doesn't block program from exiting
    self.source = source
    self.updatePeriod = updatePeriod
    self.curTemperature = 0
    self.updateTemperature()
    self.tokens = []
#--- Code snipped for brevity ---#

def processCommands(self, msg, addr) :
    cmds = msg.split(';')
    #--- Code snipped for brevity ---#
                self.tokens.append(''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))
#--- Code snipped for brevity ---#
```

Updated/Patched:

First we need to add some token management to the `__init__()`, including a `max_tokens` of 10 and a token time to live value in seconds (`token_ttl_seconds`) defaulted to an hour or 3600 seconds. 
We also update the tokens list to a tokens dictionary were we can store a key value pairs of the tokens and their expiration time. 

```python
    def __init__ (self, source, updatePeriod, port, max_tokens=10, token_ttl_seconds=3600) :
        threading.Thread.__init__(self, daemon = True) 
        #set daemon to be true, so it doesn't block program from exiting
        self.source = source
        self.updatePeriod = updatePeriod
        self.curTemperature = 0
        self.updateTemperature()
        ## update to tokens to limit
        #self.tokens = []  # Old code that can be removed.
        self.max_tokens = max_tokens  # Maximum active sessions allowed defaults to 10
        self.token_ttl = token_ttl_seconds  # Expiration window defaults to 1 hour
        self.tokens = {}  # Dictionary: token_string -> expiry_timestamp
        self.token_lock = threading.Lock()  # Thread-safety lock
#--- Code snipped for brevity ---#
```

We are also going to build a helper function to deal with clearing out expired tokens.

```python
    def _clean_expired_tokens(self):
        """Internal helper to remove expired tokens (Must be called inside lock)."""
        now = time.time()
        expired = [tok for tok, expiry in self.tokens.items() if now > expiry]
        for tok in expired:
            del self.tokens[tok]
```

And more fixes to the `processCommands()`.

We now do a check to remove expired tokens, enforce the maximum token limit, and store the new token with it's expiration time.
When a user logs out, we have revised the removal of the used token.

```python
    def processCommands(self, msg, addr) :
        cmds = msg.split(';')
        for c in cmds :
            cs = c.split(' ')
            if len(cs) == 2 : #should be either AUTH or LOGOUT
                if cs[0] == "AUTH":
                    # Replace Hardcoded Password with auth_secret from .env, and use hmac.compare_digest() to prevent timing attack.
                    if hmac.compare_digest(cs[1], self.auth_secret) :
                        with self.token_lock:
                            # Remove expired tokens to prevent memory issues
                            self._clean_expired_tokens()
                            # enforce maximum token limit
                            if len(self.tokens) >= self.max_tokens:
                                self.serverSocket.sendto(b"Server at Capacity\n", addr)
                                continue
                            # Create New Token.
                            new_token = (''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))

                            # Store token with their expiration timestamp
                            self.tokens[new_token] = time.time() + self.token_ttl

                            self.serverSocket.sendto(new_token.encode("utf-8"), addr)
                    else:
                        self.serverSocket.sendto("Incorrect password".encode("utf-8"), addr)
                elif cs[0] == "LOGOUT":
                    with self.token_lock:
                        token_to_remove = cs[1]
                        # remove token after logout
                        if token_to_remove in self.tokens:
                            del self.tokens[token_to_remove]
                else : #unknown command
                    self.serverSocket.sendto(b"Invalid Command\n", addr)
```

### Summary

Using a list to store `tokens` is not an ideal solution. 
Instead we want a solution that allows for token management and storage.
To this end, we upgraded our token list to a token dictionary that includes a time to live timestamp as part of it's key value pair.
We have limited the number of tokens to 10, and set our TTL to 60 mins (in seconds). 
Our code keeps the multithread approach that is part of the init function. 

We also built a helper function that sweeps the token dictionary, and removes any expired tokens. 

In the future, we are going to address the use of `random` for token generation instead of a more cryptographically secure library like `secrets`.

NOTES:  Update the way tokens are generated.
`random` library uses a PRNG.
We should use the `secrets` library, as it is more cryptographically secure.
```python
# Generate cryptographically strong random token
# (secrets module is preferred over random for tokens)
import secrets

new_token = secrets.token_hex(16)  # 32 hex characters
```

These replace:
```python
new_token = (''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))
```

## 3. Plaintext authentication token and authentication

We need to handle the authentication for our client and server.
Because of the architecture of this application, we have opted to use DTLS to secure the DGRAM currently used. 
(We are aware of TLS and have a route to implement, but have not gone that way at this time.)

Pythons built in `ssl` library does not support DTLS, so because of our choice, we are going to use the `pyOpenSSL` package and library for our codebase.
This package continues to be maintained, with the last update happening in 2026.

We are also going to want to enforce TLS for the flask app, so we will be handling that too.

### SampleNetworkClient.py

1. Install package 

```shell
pip install pyOpenSSL
```
(We will update `requirements.txt` so this will be handled when deploying the flask app)


and import library:

```python
from OpenSSL import SSL
```


2. Update functions that require DTLS sockets.

Original functions that used `s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)`
   1. getTemperatureFromPort()
   2. authenticate()
   3. setTemperatureC()
   4. setTemperatureF()
   5. setTemperatureK()

Updated each of these functions with DTLS Sockets code:
```python
ctx = SSL.Context(SSL.DTLS_METHOD)
raw_s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s = SSL.Connection(ctx, raw_s)
s.connect(("127.0.0.1", p))
```

### SampleNetworkServer.py

1. Add the pyOpenSSL library to code

```python
from OpenSSL import SSL
```

2. Update `init()` to handle DTLS
```python
#        # Old Authentication
#        self.serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#        self.serverSocket.bind(("127.0.0.1", port))
#        fcntl.fcntl(self.serverSocket, fcntl.F_SETFL, os.O_NONBLOCK)

        # Initialize pyOpenSSL DTLS Context
        ctx = SSL.Context(SSL.DTLS_METHOD)
        ctx.use_certificate_file("server.crt", SSL.FILETYPE_PEM)
        ctx.use_privatekey_file("server.key", SSL.FILETYPE_PEM)
        
        raw_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        raw_socket.bind(("127.0.0.1", port))
        
        # Wrap UDP socket using pyOpenSSL Connection
        self.serverSocket = SSL.Connection(ctx, raw_socket)
        fcntl.fcntl(raw_socket, fcntl.F_SETFL, os.O_NONBLOCK)

```

### app.py

To ensure that our flask app is using https, we have to add the following lines to the end of app.py

```python
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        ssl_context=('server.crt', 'server.key')
    )
```

For our development, we also need to add some additional lines to our `.env` file.

```shell
FLASK_APP=app.py
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
FLASK_DEBUG=1
FLASK_RUN_CERT=server.crt
FLASK_RUN_KEY=server.key

INCUBATOR_AUTH_SECRET=!Q#E%T&U8i6y4r2w
```

To access these updates in `.env` in the app.py file, we are going to have to add our dotenv library and some code to the top of our file:
```python
from dotenv import load_dotenv

load_dotenv()
# Load secret key from environment variable
auth_secret = os.environ.get("INCUBATOR_AUTH_SECRET")
if not auth_secret:
    raise ValueError(
        "Authentication Error"
)
```

The flask app currently requires the `INCUBATOR_AUTH_SECRET` to be set to `!Q#E%T&U8i6y4r2w`, but as we pointed out earlier, this has been burned.

To fix this, we have updates part of our login app.route.

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='GET': # if the request is a GET we return the login page
        return render_template('login.html')
    else:
        conn = get_db_connection()
        password = request.form.get('authToken')
        #is_password, act_token = verify_password(conn, password)
        # not pulling act_token from database anymore because we are going to use auth_secret instead.
        is_password = verify_password(conn, password)

        if is_password:
            snc = SampleNetworkClient.SimpleNetworkClient(23456, 23457)
            #is_auth = snc.authenticate(23456, bytes(act_token, 'utf-8'))
            # removed act_token and used auth_secret from .env instead.
            is_auth = snc.authenticate(23456, bytes(auth_secret, 'utf-8'))
            return render_template('authenticate.html', Temp="0.00", Token=is_auth.decode('utf-8'))
        else:
        ###--- Code Snipped ---###
```

We also revised the `verify_password()`, since we want to be able to use other values for our `INCUBATOR_AUTH_SECRET`:

```python
# Verify password
def verify_password(conn, user_password):
    db_query = "SELECT * FROM users"
    db_result = conn.execute(db_query).fetchone()
    db_password = db_result[1]
    encrypted_password = encrypt_password(user_password)
    if encrypted_password == db_password:
        #act_token = db_result[2]  
        #  Not needed now that we are using the env Secret as our Server Secret
        #return True, act_token 
        #  Remove act_token, as this is no longer used anywhere.
        return True
    return False, ''
```

### Summary

We want to ensure our incubator uses DTLS when communicating, and also ensure our flask app uses https.
To enforce DTLS in our communications between server and client, we installed pyOpenSSL and updated all of the socket connections.
This took place in our SampleNetworkServer and SampleNetworkClient files.

We also wanted to use https for our web interface.
To that end, we added our server.key and server.crt and pulled them into our app.py via the `.env` file, and ensured they are used every time the flask app is deployed.

We also noticed that if we wanted to change our `INCUBATOR_AUTH_SECRET`, we would have to revise our login route. 
Here we updated the code to use the `auth_secret` from the `.env` file, and not pull the `act_token` from the database. 
This also meant some minor tweaks to the `verify_password()`.