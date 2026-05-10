def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_purs(role):
        r = role.replace("-", "_")
        return ("purs" in r) or (r == "pursuer")
    def is_ev(role):
        r = role.replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = None
    if is_purs(self_role) and not is_ev(self_role): pursuer = True
    elif is_purs(opp_role) and not is_ev(opp_role): pursuer = False
    elif is_ev(self_role) and is_purs(opp_role): pursuer = False
    if pursuer is None: pursuer = True

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx*dx + dy*dy

    target_corner = None
    if pursuer:
        tc_score = -1
        for cx, cy in corners:
            sc = d2(cx, cy, ox, oy)
            if sc > tc_score:
                tc_score = sc
                target_corner = (cx, cy)
    else:
        tc_score = 10**18
        for cx, cy in corners:
            sc = d2(cx, cy, ox, oy)
            if sc < tc_score:
                tc_score = sc
                target_corner = (cx, cy)

    best = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = d2(nx, ny, ox, oy)
        cc = max(d2(nx, ny, cx, cy) for cx, cy in corners)  # closer-to-farthest corner
        trc = d2(nx, ny, target_corner[0], target_corner[1])
        # Add a small directional preference to avoid dithering.
        dir_bias = -(abs(dx) + abs(dy)) * 0.01

        if pursuer:
            val = dist * 1.0 + trc * 0.15 + (0.02 / (cc + 1)) + dir_bias
            better = (best_val is None) or (val < best_val) or (abs(val - best_val) < 1e-9 and (dx, dy) < (best[0], best[1]))
        else:
            # Evader wants to maximize distance; also head to far corner opposite pursuer.
            val = -dist * 1.0 - (d2(nx, ny, corners[0][0], corners[0][1]) + d2(nx, ny, corners[3][0], corners[3][1])) * 0.02 + trc * 0.05 + dir_bias
            better = (best_val is None) or (val > best_val) or (abs(val - best_val) < 1e-9 and (dx, dy) < (best[0], best[1]))

        if better:
            best_val = val
            best = [dx, dy]

    return best