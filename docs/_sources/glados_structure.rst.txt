GLaDOS Structure
================
There are a few major components of GLaDOS as shows below.

GLaDOS
------

Bot
---
GLaDOS can support multiple Slack bots and applications at once. When you initialize a plugin you pass the GladosBot
object of the bot you would like to be responsible for the actions of that plugin.


Plugin
------
Every GLaDOS plugin is its own module that is imported into your main handler application. This allows GLaDOS plugins to
be community based and installed as wanted just by a simple import statement.

.. note::
    V2: Each GLaDOS Plug-in has to have the register_plugin decorator and match the Plugin Interface. The easiest way to
    do this is to use the Plugin Class that is provided with GLaDOS. In the main GLaDOS function you will have to import
    all of your plugin modules and kick off a scan for plugins. This same method applies for GLaDOS Bots.


Routing
-------
GLaDOS event routing is done in two different parts: `Route Type` and `Route`.
These two parts and sometimes the bot name combined together control how events sent to GLaDOS are
routed to the respective plugins

Route Types
~~~~~~~~~~~
Route Types represent the type of action that is being requested. One way to look at Route Types
is that they would be the first path in your API structure. For example you would configure Slack to
send *Slash* commands to ``https://slack.glados.wtf/Slash/myCommand``

- **SendMessage**: Sample action to send a message as the bot.
- **Slash**: This is the route called when a slash command is called.

.. note::
   The Route Types below use the bot name as a prefix of the route (see blow).

- **Event**: This route type is used to receive messages from subscribed events in Slack.
- **Interaction**: This route type is used to receive messages from user interactions.


Route
~~~~~
Routes represent the action that is being requested. Routes are not always included in the URL
configured in Slack.

Interactive component callbacks are an example of this. The `Request URL` of for interactive
components should be set to something like ``https://slack.glados.wtf/Interaction/myBot`` and lets
say that `action_id` is `myBottonPress` then the full route would be ``myBot_myButtonPress``

Depending on the type of action sometimes the routes will be automatically
prefixed with the bot name that is responsible for handling the request.



