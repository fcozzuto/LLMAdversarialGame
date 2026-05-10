def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower().replace("-", "_")
    opp_role = (observation.get("opponent_role") or "").lower().replace("-", "_")

    def is_purs(role): return ("purs" in role) or (role == "pursuer")
    def is_ev(role): return ("evad" in role) or (role == "evader")
    pursuer = None
    if is_purs(self_role) and not is_ev(self_role): pursuer = True
    if is_purs(opp_role) and not is_ev(opp_role): pursuer = True if pursuer is None else pursuer
    if is_ev(self_role) and is_purs(opp_role): pursuer = False
    if pursuer is None:
        pursuer = True  # deterministic fallback

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx*dx + dy*dy

    # obstacle proximity penalty (local)
    obs_list = obstacles[:]
    def obs_pen(x, y):
        p = 0
        for ox2, oy2 in obs_list:
            dd = d2(x, y, ox2, oy2)
            if dd == 0: return 10**9
            if dd <= 4: p -= 3
            elif dd <= 9: p -= 1
        return p

    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
    if pursuer:
        # pursue with slight cut-off: move toward opponent while preferring progress along opponent line
        best_move = (0,0); best_score = -10**18
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in obs: continue
            dist = d2(nx, ny, ox, oy)
            toward = abs((nx-ox) - (sx-ox)) + abs((ny-oy) - (sy-oy))  # deterministic bias
            score = -dist*10 + toward + obs_pen(nx, ny)
            if score > best_score: best_score = score; best_move = [dx, dy]
        return [best_move[0], best_move[1]]
    else:
        # evade: maximize distance; head to farthest corner from pursuer with obstacle-aware tie breaks
        far_corner = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
        best_move = (0,0); best_score = -10**18
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in obs: continue
            dist_opp = d2(nx, ny, ox, oy)
            dist_corner = d2(nx, ny, far_corner[0], far_corner[1])
            # prefer increasing distance and also moving toward far corner
            corner_bonus = -dist_corner
            score = dist_opp*10 + corner_bonus + obs_pen(nx, ny)
            if score > best_score: best_score = score; best_move = [dx, dy]
        return [best_move[0], best_move[1]]