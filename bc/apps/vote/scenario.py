class Scenario(object):
    def __init__(self, num_cands, factions, payoffs, map=None):
        self.num_cands = num_cands
        self.faction_sizes = faction_sizes
        self.voter_factions = [faction for (faction, size) in enumerate(faction_sizes) 
                                        for i in xrange(size)]
        assert len(payoffs) == num_cands
        for i in num_cands:
            assert len(payoffs[i]) == len(faction_sizes)
        self.payoffs = payoffs
        self.map = map
        
    def payoff_for(self, cand, faction):
        return self.payoffs[cand][faction]
    
    def total_payoff(self, cand):
        payoff = 0
        for faction in len(self.factions):
            payoff += self.faction_sizes[faction] * self.payoff_for(cand, faction)
        return payoff
    
    def num_factions(self):
        return len(self.faction_sizes)
    
    def faction_size(self, faction):
        return self.faction_sizes[faction]
    
    def num_voters(self):
        return len(self.voter_factions)
    
    
wcw = Scenario(3,
               (4,2,3),
               ((3,0  ,0),
                (1,3  ,2),
                (0,1.5,3))
               )

simple = Scenario(3,
                  (1,2),
                  ((4,0),
                   (3,3),
                   (0,4))
                  )

SCENARIOS = {'WCW': wcw,
             'simple': simple,
             }
