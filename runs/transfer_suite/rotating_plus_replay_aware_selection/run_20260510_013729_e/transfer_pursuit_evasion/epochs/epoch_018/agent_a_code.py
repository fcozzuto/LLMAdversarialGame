def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in role

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def nearest_obst(x, y):
        if not ob:
            return 99
        md = 99
        for px, py in ob:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    best = None
    best_val = None

    # Deterministic tie-break by move order in deltas.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in ob:
            continue

        d = manh(nx, ny)
        obst_d = nearest_obst(nx, ny)
        e = edge_dist(nx, ny)

        if pursuer:
            # Move toward opponent; avoid obstacles; slightly prefer central lanes.
            val = (-d * 20) + (obst_d * 1.6) + (e * 0.4)
        else:
            # Move away from opponent; avoid obstacles; slight preference for edges to dodge wall runners.
            val = (d * 20) + (obst_d * 1.6) + ((0.5 - e / (min(w, h) - 1 + 1e-9)) * 2.0)

        if best is None or (pursuer and val > best_val) or ((not pursuer) and val > best_val):
            best = (dx, dy)
            best_val = val

    # If all moves blocked (rare), stay put.
    return [best[0], best[1]] if best is not None else [0, 0]