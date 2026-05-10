def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (evader or pursuer):
        evader = True

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def edge_pen(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            v = -10**18 if evader else 10**18
        elif (nx, ny) in obs_set:
            v = -10**16 if evader else 10**16
        else:
            d = dist2(nx, ny)
            if (nx, ny) == (ox, oy):
                v = (10**12 if pursuer else -10**12)
            else:
                # Main objective: distance shaping depends on role
                if evader:
                    v = d * 1000 + edge_pen(nx, ny) * 5
                    # Mildly discourage moving onto squares closer than necessary
                    v -= ((nx - ox) * (sx - ox) + (ny - oy) * (sy - oy))
                else:
                    v = -d * 1000 + edge_pen(nx, ny) * 5
                    v += ((nx - ox) * (sx - ox) + (ny - oy) * (sy - oy))
                # Extra: prefer moves that change position (break ties deterministically)
                if dx == 0 and dy == 0:
                    v -= 1
        if best is None or (v > bestv if evader else v > bestv):
            best = (dx, dy)
            bestv = v

    return [int(best[0]), int(best[1])]