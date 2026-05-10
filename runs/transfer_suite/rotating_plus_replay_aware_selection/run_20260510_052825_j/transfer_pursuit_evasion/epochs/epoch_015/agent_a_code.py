def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obs_list if isinstance(p, (list, tuple)) and len(p) >= 2}
    resources = observation.get("resources", []) or []
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    def is_ev(r):
        r = (r or "").replace("-", "_")
        return ("evad" in r) or (r == "evader")
    def is_pu(r):
        r = (r or "").replace("-", "_")
        return ("purs" in r) or (r == "pursuer")

    pursuer = True
    if is_pu(self_role) and not is_ev(self_role):
        pursuer = True
    elif is_pu(opp_role) and not is_ev(opp_role):
        pursuer = False

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    corners = ((0, 0), (0, h-1), (w-1, 0), (w-1, h-1))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def d2(ax, ay, bx, by): dx = ax - bx; dy = ay - by; return dx*dx + dy*dy

    best_move = (0, 0); best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        score = 0
        dist_opp = d2(nx, ny, ox, oy)
        if pursuer:
            score += -dist_opp * 5
        else:
            score += dist_opp * 5
        if res:
            score += -min(d2(nx, ny, rx, ry) for rx, ry in res) * (1 if pursuer else -1)
        else:
            cx, cy = max(corners, key=lambda c: d2(nx, ny, c[0], c[1]))
            score += d2(nx, ny, cx, cy) * (0.2 if not pursuer else -0.2)
        if best_score is None or score > best_score:
            best_score = score; best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]