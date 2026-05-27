def choose_move(observation):
    # Defensive defaults
    dx = 0
    dy = 0

    def get_int(v, default=0):
        try:
            if isinstance(v, (int, float)):
                return int(v)
        except Exception:
            pass
        return default

    if isinstance(observation, dict):
        goal = None

        # Resource collection: resource.direction
        resource = observation.get('resource')
        if isinstance(resource, dict):
            goal = resource.get('direction')
            if isinstance(goal, (list, tuple)) and len(goal) >= 2:
                dx = get_int(goal[0], 0)
                dy = get_int(goal[1], 0)

        # If not found, try 'goal'
        if goal is None:
            g = observation.get('goal')
            if isinstance(g, (list, tuple)) and len(g) >= 2:
                dx = get_int(g[0], 0)
                dy = get_int(g[1], 0)

        # Pursuit/Evasion: opponent vector
        if dx == 0 and dy == 0:
            opp = observation.get('opponent')
            if isinstance(opp, dict):
                dirv = opp.get('direction')
                if isinstance(dirv, (list, tuple)) and len(dirv) >= 2:
                    dx = get_int(dirv[0], 0)
                    dy = get_int(dirv[1], 0)

        # Territory control: claim direction
        if dx == 0 and dy == 0:
            claim = observation.get('claim')
            if isinstance(claim, dict):
                dirv = claim.get('direction')
                if isinstance(dirv, (list, tuple)) and len(dirv) >= 2:
                    dx = get_int(dirv[0], 0)
                    dy = get_int(dirv[1], 0)

    # Fallback: deterministic small set, chosen to be robust across schemas
    if dx == 0 and dy == 0:
        for cand in [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
            dx, dy = cand
            break

    # Clamp to allowed range
    if dx not in (-1,0,1) or dy not in (-1,0,1):
        dx, dy = 0, 0

    return [dx, dy]
