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

    pursuer = is_purs(self_role) and not is_ev(self_role)
    if not pursuer and is_purs(opp_role) and not is_ev(opp_role):
        pursuer = True
    elif is_ev(self_role) and is_purs(opp_role):
        pursuer = False
    if not self_role and not opp_role:
        pursuer = True

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx*dx + dy*dy
    def step_val(nx, ny):
        return d2(nx, ny, ox, oy)

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        v = step_val(nx, ny)
        if pursuer:
            # minimize distance; slight bias to progress (lower abs dx/dy to opponent)
            bias = abs(nx - ox) + abs(ny - oy)
            key = (v, bias, nx, ny)
            if best is None or key < best:
                best = key
                best_val = [dx, dy]
        else:
            # maximize distance; slight bias to move toward far corner away from opponent
            vcorner = abs(nx - (w-1 if ox < w//2 else 0)) + abs(ny - (h-1 if oy < h//2 else 0))
            key = (-v, -vcorner, -nx, -ny)
            if best is None or key < best:
                best = key
                best_val = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_val