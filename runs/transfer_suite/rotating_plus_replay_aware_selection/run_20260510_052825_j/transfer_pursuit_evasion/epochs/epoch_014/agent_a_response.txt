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
    if is_purs(self_role) and not is_ev(self_role):
        pursuer = True
    elif is_purs(opp_role) and not is_ev(opp_role):
        pursuer = False
    if pursuer is None:
        pursuer = True

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx*dx + dy*dy
    def manh(ax, ay, bx, by):
        return abs(ax-bx) + abs(ay-by)
    def near_obs_score(x, y):
        # small deterministic penalty if adjacent to obstacles
        s = 0
        for (px, py) in obs:
            if abs(px-x) + abs(py-y) == 1:
                s -= 1
        return s

    best = None
    if pursuer:
        # chase greedily; also prefer moves that head toward the farthest corner from opponent (helps cut off)
        far_corner = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            sd = d2(nx, ny, ox, oy)
            # bonus for reducing distance while making progress toward far_corner from opponent perspective
            sc = (sd, manh(nx, ny, ox, oy), -manh(nx, ny, far_corner[0], far_corner[1]))
            if best is None or sc < best[0]:
                best = (sc, [dx, dy])
        if best is not None:
            return best[1]
    else:
        # evade greedily; maximize distance from pursuer, avoid obstacles; bias toward the corner farthest from pursuer
        target_corner = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            sd = d2(nx, ny, ox, oy)
            # encourage moving toward chosen corner when distances tie
            sc = (-sd, -manh(nx, ny, ox, oy), manh(nx, ny, target_corner[0], target_corner[1]), -near_obs_score(nx, ny))
            if best is None or sc < best[0]:
                best = (sc, [dx, dy])
        if best is not None:
            return best[1]

    # If all moves blocked, or role ambiguity, do minimal deterministic safe fallback: try stay; else first valid.
    if inb(sx, sy) and (sx, sy) not in obs:
        return [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]