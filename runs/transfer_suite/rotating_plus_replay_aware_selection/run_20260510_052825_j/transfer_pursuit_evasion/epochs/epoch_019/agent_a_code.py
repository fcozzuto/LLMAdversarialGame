def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower().replace("-", "_")
    opp_role = (observation.get("opponent_role") or "").lower().replace("-", "_")
    pursuer = ("purs" in role) or (role == "pursuer")
    evader = ("evad" in role) or (role == "evader")
    if "purs" in opp_role and not evader:
        pursuer = False
    if evader and not ("purs" in opp_role):
        pursuer = False
    if ("purs" not in role and "evad" not in role) and (("purs" in opp_role) or ("evad" in opp_role)):
        pursuer = ("evad" in opp_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best_dx, best_dy = 0, 0
    best_val = -10**30

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        opp_dist = d2(nx, ny, ox, oy)
        if res:
            tdist = min(d2(nx, ny, rx, ry) for rx, ry in res)
        else:
            tdist = 0
        if pursuer:
            val = -tdist * 3 + opp_dist * 0.5
        else:
            val = tdist * 2 + opp_dist * 3
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy
    return [best_dx, best_dy]