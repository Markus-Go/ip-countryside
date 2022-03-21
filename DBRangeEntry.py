class DBRangeEntry:

    ipFrom   = -1
    ipTo     = -1
    country  = None
    registry = None

    def __init__(self, ipFrom, ipTo, country , registry) -> None:
        self.ipFrom   = ipFrom 
        self.ipTo     = ipTo
        self.country  = country
        self.registry = registry
    
    def __str__(self) -> str:
        
        return f"""
        ipFrom:     {self.ipFrom}
        ipTo:       {self.ipTo}
        country:    {self.country}
        registry:   {self.registry}""" 