def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if (sx, sy) in obst or not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick the resource where we are relatively closer than opponent.
    # Neighboring opponent-resource players typically chase minimal opponent distance;
    # we counter by selecting maximal (opp_dist - self_dist).
    best_t = None
    best_key = None
    for tx, ty in res:
        sd = man((sx, sy), (tx, ty))
        od = man((ox, oy), (tx, ty))
        # maximize advantage; break ties by smaller self distance, then by coords
        key = (od - sd, -sd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)
    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            # primary: move closer to target
            nd_t = man((nx, ny), (tx, ty))
            # secondary: increase separation so opponent is less likely to reach same resource first
            nd_o = man((nx, ny), (ox, oy))
            # tertiary: tie-break by lexicographic move to keep determinism
            candidates.append((nd_t, -nd_o, dx, dy))
        else:
            # invalid moves: engine keeps position; treat as large distance (discourage)
            candidates.append((10**9, 10**9, dx, dy))

    # Choose candidate with smallest distance to target; among them maximize separation.
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]