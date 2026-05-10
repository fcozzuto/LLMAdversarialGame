def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    role = str(observation.get("self_role", "")).lower()
    evader = ("evad" in role) or ("run" in role) or ("esc" in role)
    pursuer = ("purs" in role) or ("catch" in role) or ("pred" in role)
    if not evader and not pursuer:
        pursuer = True

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_obst(x, y):
        if not obs:
            return 999
        best = 999
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18 if pursuer else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d0 = dist(sx, sy, ox, oy)
        d1 = dist(nx, ny, ox, oy)
        obst = min_obst(nx, ny)
        if pursuer:
            val = (d0 - d1) * 1000 + obst
            if val > best_val:
                best_val, best_move = val, (dx, dy)
        else:
            val = (d1 - d0) * 1000 + obst
            if val > best_val:
                best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]