def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    pref_order = {
        (0, 0): 0, (0, -1): 1, (1, 0): 2, (0, 1): 3, (-1, 0): 4,
        (-1, -1): 5, (1, -1): 6, (-1, 1): 7, (1, 1): 8
    }

    r = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in r) or ("chaser" in r) or ("hunter" in r)

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_tuple = None

    cur_d = manhattan(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = manhattan(nx, ny, ox, oy)

        # Deterministic "space" bonus: prefer moves that keep options (avoid tight spots)
        free_neighbors = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if legal(tx, ty):
                free_neighbors += 1

        # Heuristic objective: pursuer minimizes distance; evader maximizes distance.
        # Add small tie-breakers based on distance change and mobility.
        dist_term = d - cur_d
        if pursuer:
            obj = (d, abs(dist_term), -free_neighbors, pref_order[(dx, dy)])
            better = best_tuple is None or obj < best_tuple
        else:
            obj = (-d, abs(dist_term), -free_neighbors, pref_order[(dx, dy)])
            better = best_tuple is None or obj < best_tuple

        if better:
            best_tuple = obj
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]