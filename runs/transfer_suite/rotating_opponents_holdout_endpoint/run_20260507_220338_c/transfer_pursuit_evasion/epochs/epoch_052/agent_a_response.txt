def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    wants_capture = any(k in role_s for k in ("purs", "catch", "capture", "hunter", "seeker", "chase"))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def man(x, y):
        return abs(ox - x) + abs(oy - y)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    best = None
    best_key = None
    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = cheb(nx, ny)
        dist_m = man(nx, ny)
        if wants_capture:
            # minimize distance to opponent; also prefer moving closer in manhattan for ties
            corner_bonus = -min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            key = (d, dist_m, corner_bonus, dx, dy)
        else:
            # maximize distance to opponent; prefer running toward farthest corner for ties
            corner_f = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            key = (-d, -dist_m, corner_f, -dx, -dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]