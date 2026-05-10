def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower().replace("-", "_")
    opp_role = (observation.get("opponent_role") or "").lower().replace("-", "_")

    def is_purs(role):
        return ("purs" in role) or (role == "pursuer")
    def is_ev(role):
        return ("evad" in role) or (role == "evader")

    pursuer = None
    if is_purs(self_role) and not is_ev(self_role):
        pursuer = True
    elif is_purs(opp_role) and not is_ev(opp_role):
        pursuer = False
    elif is_ev(self_role) and is_purs(opp_role):
        pursuer = False
    if pursuer is None:
        pursuer = True

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx*dx + dy*dy
    def corner_score(nx, ny):
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        return max(d2(nx, ny, cx, cy) for cx, cy in corners)

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        dist = d2(nx, ny, ox, oy)
        if pursuer:
            # Go to reduce distance; also prefer staying away from obstacles/edges if tied
            val = -dist + 0.01 * corner_score(nx, ny)
        else:
            # Evade by increasing distance and also pushing toward farthest corner from pursuer
            val = dist + 0.05 * corner_score(nx, ny)

        # Tie-break deterministically toward minimal dx,dy lexicographic preference
        if best_score is None or val > best_score or (val == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = val
            best_move = [dx, dy]

    return best_move