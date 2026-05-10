def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in res:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        key = (do - ds, -ds, -rx, -ry)  # maximize advantage; then nearer to self
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    cx = 1 if tx > sx else (-1 if tx < sx else 0)
    cy = 1 if ty > sy else (-1 if ty < sy else 0)

    candidates = [(cx, cy), (cx, 0), (0, cy), (cx, -cy), (-cx, cy), (0, 0)]
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [int(dx), int(dy)]

    return [0, 0]