def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))
    scores = observation.get("scores") or {}
    self_name = observation.get("self_name", "agent_a")
    opponent_name = observation.get("opponent_name", "agent_b")
    my_score = float(scores.get(self_name, 0.0) or 0.0)
    op_score = float(scores.get(opponent_name, 0.0) or 0.0)

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
    if resources:
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = abs(sx - rx) + abs(sy - ry)
            if d < bestd or (d == bestd and (rx, ry) < best):
                bestd, best = d, (rx, ry)
        tx, ty = best
    elif my_score < op_score:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dres = 0
        if resources:
            mdres = 10**9
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    mdres = 0
                    break
                dd = abs(nx - rx) + abs(ny - ry)
                if dd < mdres:
                    mdres = dd
            dres = -mdres
        else:
            dres = - (abs(nx - tx) + abs(ny - ty))
        center_bonus = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.01
        goal_bonus = - (abs(nx - tx) + abs(ny - ty))
        val = dres + center_bonus + goal_bonus * 0.1
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]