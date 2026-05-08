def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    is_pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role)

    def open_moves_count(x, y):
        c = 0
        for ddx, ddy in dirs:
            nx, ny = x + ddx, y + ddy
            if free(nx, ny):
                c += 1
        return c

    best = None
    best_score = None
    for nx, ny, dx, dy in candidates:
        d = dist2(nx, ny, ox, oy)
        exits = open_moves_count(nx, ny)
        corner_d = max(dist2(cx, cy, ox, oy) for cx, cy in corners)  # constant for this turn
        # Additional corner bias for evader: move toward the corner farthest from opponent
        best_corner = None
        if corners:
            best_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        corner_push = 0
        if best_corner:
            corner_push = dist2(nx, ny, best_corner[0], best_corner[1])

        if is_pursuer:
            # minimize distance; prefer positions with more mobility
            score = -d + 0.03 * exits - 0.001 * corner_push
        else:
            # maximize distance; prefer moving toward the target corner and keep mobility
            score = d + 0.06 * exits - 0.001 * corner_push + 0.0001 * corner_d

        if best is None or (score > best_score):
            best = (dx, dy)
            best_score = score

    return [int(best[0]), int(best[1])]