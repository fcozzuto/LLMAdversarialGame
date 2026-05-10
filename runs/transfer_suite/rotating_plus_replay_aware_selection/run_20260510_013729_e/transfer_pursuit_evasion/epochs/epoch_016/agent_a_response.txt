def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.append((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in role

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18 if pursuer else -10**18

    def edge_score(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def obst_min_dist(x, y):
        if not ob:
            return 99
        md = 99
        for px, py in ob:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if any(nx == px and ny == py for px, py in ob):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        es = edge_score(nx, ny)
        md = obst_min_dist(nx, ny)

        if pursuer:
            val = (-dist) * 100 + es * 2 + md
        else:
            val = (dist) * 100 + es * 3 - (0 if md >= 6 else (6 - md) * 2)

        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move