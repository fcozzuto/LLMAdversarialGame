def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursur" in role) or ("catch" in role) or ("hunter" in role)
    evader = ("evad" in role) or ("runner" in role) or ("flee" in role) or (not pursuer)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: man(sx, sy, c[0], c[1])) if evader else min(corners, key=lambda c: man(sx, sy, c[0], c[1]))

    best = (None, -10**18 if evader else 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        corner_bias = -man(nx, ny, best_corner[0], best_corner[1]) if evader else man(nx, ny, best_corner[0], best_corner[1])
        score = d + 0.05 * corner_bias if evader else (-d + 0.05 * corner_bias)
        if best[0] is None:
            best = ((dx, dy), score)
        else:
            if evader:
                if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
                    best = ((dx, dy), score)
            else:
                if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
                    best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]