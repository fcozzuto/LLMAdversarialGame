def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    selfT = set(map(tuple, observation.get("self_territory") or []))
    oppT = set(map(tuple, observation.get("opponent_territory") or []))

    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px
            sy += py
        tx, ty = sx // n, sy // n
    else:
        tx, ty = ox, oy

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        a = ax - bx
        if a < 0:
            a = -a
        b = ay - by
        if b < 0:
            b = -b
        return a + b

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    my_score = (observation.get("scores") or {}).get("self", observation.get("self_score", 0))
    opp_score = (observation.get("scores") or {}).get("opponent", observation.get("opponent_score", 0))
    k = 2 if my_score >= opp_score else 1

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dist_to_opp = man(nx, ny, tx, ty)
        dist_to_opppos = man(nx, ny, ox, oy)
        own_bonus = 3 if (nx, ny) in selfT else 0
        val = -k * dist_to_opp - dist_to_opppos + own_bonus
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best