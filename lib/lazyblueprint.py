from flask import Blueprint

class LazyBlueprint(Blueprint):
    def __init__(self, name, import_name, static_folder=None,
                 static_url_path=None, template_folder=None,
                 url_prefix=None, subdomain=None, url_defaults=None):
        super(LazyBlueprint, self).__init__(name, import_name, static_folder,
                 static_url_path, template_folder,
                 url_prefix, subdomain, url_defaults)
        self.views = '.'.join([import_name,'views'])
        print import_name, self.views
        self.lazyrules = []
        self.states = []
        self.record(self.setuplazyload)
    
    def setuplazyload(self, state):
        self.lazyrules.append(state.add_url_rule('/<path:endpoint>', 'index', self.lazyloadfor(state)))
        self.lazyrules.append(state.add_url_rule('/', 'index', self.lazyloadfor(state),
                                                  defaults={'endpoint':''}))
        self.states.append(state)
        
    def lazyloadfor(self, state):
        def innerlazyload(endpoint, **kw):
            for rule in self.lazyrules:
                print "rule is ",rule
                rule.remove()
            print "rules removed"
            self.base_functions, self.deferred_functions = self.deferred_functions, []
            __import__(self.views)
            
            state.app.debug, debug = False, state.app.debug #don't trigger setupfunction warnings
            for fixstate in self.states:
                for deferred in self.deferred_functions:
                    deferred(fixstate)
            state.app.debug = debug
            self.deferred_functions = self.base_functions + self.deferred_functions
            print "now redispatching"
            return self.redispatch(state, endpoint, **kw)
        return innerlazyload
        
    def redispatch(self, state, endpoint, **kw):
        return state.app.full_redispatch_request()