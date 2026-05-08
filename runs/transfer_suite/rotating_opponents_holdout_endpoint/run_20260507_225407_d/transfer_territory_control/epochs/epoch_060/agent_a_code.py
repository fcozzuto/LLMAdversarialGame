def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def norm_pos(p):
        if not p or len(p) < 2:
            return None
        x, y = int(p[0]), int(p[1])
        return (x, y) if 0 <= x < w and 0 <= y < h else None

    resources = [norm_pos(p) for p in (observation.get("resources") or [])]
    resources = [p for p in resources if p is not None]

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        q = norm_pos(p)
        if q is not None:
            unclaimed.add(q)

    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target = None
    if resources:
        target = min(resources, key=lambda p: dist2((sx, sy), p))
    else:
        if unclaimed:
            best = None
            bestd = 10**18
            for dx, dy in neigh:
                x, y = sx + dx, sy + dy
                if ok(x, y) and (x, y) in unclaimed:
                    d = dist2((x, y), (ox, oy))
                    if d < bestd:
                        bestd = d
                        best = (x, y)
            if best is not None:
                target = best

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in neigh:
        x, y = sx + dx, sy + dy
        if not ok(x, y):
            continue
        if target is not None:
            score = -dist2((x, y), target)
        else:
            score = -dist2((x, y), (ox, oy))
        if (x, y) in unclaimed:
            score += 1000
        if (x, y) == (ox, oy):
            score += 5000
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move