def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursu" in role) or ("chase" in role) or ("capt" in role)
    evader = ("evad" in role) or ("escap" in role)
    if not pursuer and evader:
        pursuer = False
    if not pursuer and not evader:
        pursuer = True

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    pref = {(-1, -1): 0, (0, -1): 1, (1, -1): 2, (-1, 0): 3, (0, 0): 4, (1, 0): 5, (-1, 1): 6, (0, 1): 7, (1, 1): 8}

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def obst_near_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs_set:
                    pen += 2 if dx == 0 or dy == 0 else 3
        return pen

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        d = dist2(nx, ny)
        pen = obst_near_pen(nx, ny)
        if pursuer:
            v = d * 1000 + pen
            better = bestv is None or v < bestv or (v == bestv and pref[(dx, dy)] < pref[best])
        else:
            v = -d * 1000 + pen
            better = bestv is None or v > bestv or (v == bestv and pref[(dx, dy)] < pref[best])
        if better:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]