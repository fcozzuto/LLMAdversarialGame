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

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("pursuit" in role) or ("evader" not in role and role != "evader")

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_dist(start, goal, maxd=10):
        if start == goal:
            return 0
        if not inb(start[0], start[1]) or not inb(goal[0], goal[1]):
            return None
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
                dist[(nx, ny)] = d + 1
                if (nx, ny) == goal:
                    return d + 1
                q.append((nx, ny))
        return None

    def mhd2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = bfs_dist((nx, ny), (ox, oy), maxd=10)
        if d is None:
            approx = mhd2(nx, ny) ** 0.5
        else:
            approx = d
        # pursuer: minimize path distance; evader: maximize
        val = approx
        # tie-break: for pursuer prefer reducing axis gaps; for evader prefer increasing
        axis_gap = abs(nx - ox) + abs(ny - oy)
        if is_pursuer:
            val = (val, axis_gap, abs(dx) + abs(dy))
            pick = (best_val is None) or (val < best_val)
        else:
            val = (-val, -axis_gap, abs(dx) + abs(dy))
            pick = (best_val is None) or (val > best_val)
        if pick:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]