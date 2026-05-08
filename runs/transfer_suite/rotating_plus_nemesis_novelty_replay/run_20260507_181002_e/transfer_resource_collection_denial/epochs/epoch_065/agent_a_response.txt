def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = pos(observation.get("self_position", None), (0, 0))
    ox, oy = pos(observation.get("opponent_position", None), (sx, sy))

    obs = set()
    for o in observation.get("obstacles", []) or []:
        x, y = pos(o, None)
        if x is not None and 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = pos(r, None)
        if x is not None and free(x, y):
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource that we can reach first (or at least threaten)
    best_t = None
    best_key = None
    for t in resources:
        key = (man((ox, oy), t) - man((sx, sy), t), -man((sx, sy), t), t[0], t[1])
        if best_key is None or key > best_key:
            best_key, best_t = key, t

    t = best_t

    def opp_next_from(px, py):
        # Opponent likely heads for its closest resource; approximate by greedily minimizing distance to target t.
        best = (10**9, px, py)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = px + dx, py + dy
                if free(nx, ny):
                    d = man((nx, ny), t)
                    if d < best[0] or (d == best[0] and (nx, ny) < (best[1], best[2])):
                        best = (d, nx, ny)
        return best[1], best[2]

    o2x, o2y = opp_next_from(ox, oy)

    best_move = (0, 0)
    best_val = (-10**9, 10**9)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            self_d = man((nx, ny), t)
            opp_d = man((o2x, o2y), t)
            # Favor getting to t first; if tie, prefer closer absolute; slight preference for increasing opponent distance.
            val = (opp_d - self_d, -self_d, dx, dy)
            if val > (best_val[0], -best_val[1], -10**9, -10**9) or best_val == (-10**9, 10**9):
                best_val = (val[0], -val[1])
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]