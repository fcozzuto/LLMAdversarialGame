def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        cx, cy = (w - 1) / 2, (h - 1) / 2
        best, bestv = [0, 0], -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                d = max(abs(nx - cx), abs(ny - cy))
                v = -d
                if v > bestv:
                    bestv, best = v, [dx, dy]
        return best

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev, diagonal allowed

    res = resources
    # Pick a target resource, preferring ones where we arrive earlier or deny opponent.
    best_t, best_score = res[0], -10**9
    for r in res:
        sd, od = dist((sx, sy), r), dist((ox, oy), r)
        # Primary: deny (maximize od-sd); Secondary: prefer closer; Tertiary: tie-break by coords.
        score = (od - sd) * 100 - sd * 3 - r[0] * 0.01 - r[1] * 0.001
        if score > best_score:
            best_score, best_t = score, r

    tx, ty = best_t
    options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                options.append((dx, dy, nx, ny))

    # If we can capture immediately, do it.
    if (sx, sy) in set(tuple(p) for p in res):
        return [0, 0]

    # Evaluate next moves: move toward target, avoid stepping into opponent proximity, and try to deny.
    best_move, bestv = [0, 0], -10**18
    for dx, dy, nx, ny in options:
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        deny = (d_opp - d_self)
        # Also reduce chance of walking into opponent's immediate reach.
        opp_reach = dist((nx, ny), (ox, oy))
        v = deny * 50 - d_self * 2 - opp_reach * 0.5
        if (nx, ny) in set(tuple(p) for p in res):
            v += 1000
        # Slight preference for staying within bounds already satisfied; deterministic tie-break.
        if v > bestv or (v == bestv and (dx, dy) < (best_move[0], best_move[1])):
            bestv, best_move = v, [dx, dy]
    return best_move