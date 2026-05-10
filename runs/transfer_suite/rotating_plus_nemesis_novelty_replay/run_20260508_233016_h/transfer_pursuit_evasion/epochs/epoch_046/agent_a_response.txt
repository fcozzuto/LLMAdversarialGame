def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("pursuit" in role) or ("evader" not in role and role == "")

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_dist(start, goal, maxd=6):
        if start == goal:
            return 0
        q = [start]
        dist = {start: 0}
        i = 0
        while i < len(q):
            x, y = q[i]
            d = dist[(x, y)]
            i += 1
            if d >= maxd:
                continue
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in dist:
                    continue
                nd = d + 1
                dist[(nx, ny)] = nd
                if (nx, ny) == goal:
                    return nd
                q.append((nx, ny))
        if goal in dist:
            return dist[goal]
        # fallback: optimistic (still deterministic)
        return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

    # Evaluate candidate next positions
    # pursuer: minimize path distance to opponent; evader: maximize it.
    best = None
    best_score = None
    center_bias = (abs(sx - (w - 1) / 2.0) + abs(sy - (h - 1) / 2.0)) * 1e-3
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = bfs_dist((nx, ny), (ox, oy), maxd=6)
        # tie-breaker: prefer moves that increase/decrease center distance slightly
        cb = (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 1e-3
        # Score: higher is better.
        score = (-d if is_pursuer else d) + (-cb if is_pursuer else cb) - center_bias
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]