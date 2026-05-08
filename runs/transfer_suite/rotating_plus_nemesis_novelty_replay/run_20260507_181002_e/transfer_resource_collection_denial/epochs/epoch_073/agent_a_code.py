def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Heuristic: maximize advantage over opponent for the best contestable resource.
        # Collecting (distance 0) dominates; else prefer increasing (opp_dist - self_dist_next).
        s_next = 0
        for (rx, ry) in res:
            d_self = md(nx, ny, rx, ry)
            if d_self == 0:
                val = 10**6
            else:
                d_opp = md(ox, oy, rx, ry)
                # Encourage resources where opponent is relatively farther, but also slightly prefer closeness.
                val = (d_opp - d_self) * 100 - d_self
            if val > s_next:
                s_next = val

        # Tie-break: slightly prefer moves that reduce own distance to the nearest resource.
        nearest_now = min(md(sx, sy, rx, ry) for (rx, ry) in res)
        nearest_next = min(md(nx, ny, rx, ry) for (rx, ry) in res)
        tie = (nearest_now - nearest_next) * 10

        score = s_next + tie
        if score > best_score:
            best_score = score
            best_move = [nx - sx, ny - sy]

    return [int(best_move[0]), int(best_move[1])]