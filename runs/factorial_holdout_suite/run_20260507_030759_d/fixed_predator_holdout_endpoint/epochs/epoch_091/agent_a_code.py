def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        deny = 1 if sd <= od else 0
        # Prefer resources we can reach no later than opponent; among those, shortest self distance.
        # If none can be denied, prefer resources where opponent is relatively farther (largest od - sd),
        # and secondarily smallest self distance.
        key = (deny, sd if deny else (od - sd), -od if deny else -od, -(rx * 100 + ry))
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
        if 0 <= sx + dx < w and (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if 0 <= sy + dy < h and (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]
    return [dx, dy]