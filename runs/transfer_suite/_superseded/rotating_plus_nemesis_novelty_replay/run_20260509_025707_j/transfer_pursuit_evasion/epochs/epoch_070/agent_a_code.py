def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_pursuer(role):
        r = (role or "").lower()
        return ("pursuer" in r) or ("chaser" in r) or ("pursuit" in r) or ("hunter" in r)

    self_pursuer = is_pursuer(observation.get("self_role"))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    if self_pursuer:
        target_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        tx, ty = target_corner
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            # Secondary: improve capture geometry by moving toward chosen corner
            v = v * 1000 + dist2(nx, ny, tx, ty)
            if best_val is None or v < best_val:
                best_val = v
                best_move = (dx, dy)
    else:
        # Evader: maximize distance from pursuer with a slight wall/obstacle bias away from trap corners
        bad_corner = min(corners, key=lambda c: dist2(c[0], c[1], sx, sy))
        bx, by = bad_corner
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            # Secondary: avoid drifting into "bad" corner
            v = v * 1000 - dist2(nx, ny, bx, by)
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]