def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_pursuer(role):
        r = (role or "").replace("-", "_")
        return ("purs" in r) or (r == "pursuer")
    def is_evader(role):
        r = (role or "").replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = is_pursuer(self_role) and not is_evader(self_role)
    if not pursuer:
        if is_pursuer(opp_role) and not is_evader(opp_role):
            pursuer = True
        elif is_pursuer(opp_role) and is_evader(opp_role):
            pursuer = False
    if pursuer and is_evader(self_role):
        pursuer = False

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    corners = [(0,0),(w-1,0),(w-1,h-1),(0,h-1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(x1,y1,x2,y2):
        dx = x1 - x2; dy = y1 - y2
        return dx*dx + dy*dy
    def man(x1,y1,x2,y2):
        return abs(x1-x2) + abs(y1-y2)

    tx = ty = None
    if not pursuer:
        # evasion_corner: commit to the farthest corner from pursuer while moving there
        best = None
        for cx, cy in corners:
            score = man(ox, oy, cx, cy) - 0.25*man(sx, sy, cx, cy)
            key = (-score, cx, cy)
            if best is None or key < best:
                best = key; tx, ty = cx, cy
    else:
        # pursuer: chase directly; slight bias toward cutting angles by aiming at opponent's farthest corner
        farcx = farcy = corners[0]
        best = None
        for cx, cy in corners:
            score = d2(ox, oy, cx, cy)
            key = (-score, cx, cy)
            if best is None or key < best:
                best = key; farcx, farcy = cx, cy
        tx, ty = farcx, farcy

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        dist_opp = d2(nx, ny, ox, oy)
        dist_corner = d2(nx, ny, tx, ty)
        if pursuer:
            key = (dist_opp, 0.02*dist_corner, dx, dy)
        else:
            # prioritize staying far from pursuer, while heading to chosen corner
            key = (-dist_opp, 0.02*dist_corner, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_key is not None else [0, 0]