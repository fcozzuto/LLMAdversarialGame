def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_r = None
        best_d = 10**9
        for r in resources:
            try:
                rx, ry = int(r[0]), int(r[1])
            except Exception:
                continue
            if not inb(rx, ry):
                continue
            d = man(sx, sy, rx, ry)
            if d < best_d:
                best_d = d
                best_r = (rx, ry)
        tx, ty = best_r if best_r is not None else ((w - 1) // 2, (h - 1) // 2)
    else:
        tx, ty = ((w - 1) // 2, (h - 1) // 2)

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        score -= man(nx, ny, tx, ty) * 3
        score += (man(nx, ny, ox, oy) >= 3) * 2
        score += man(nx, ny, ox, oy)
        # Prefer not to stand still if any move reduces distance to target
        if (dx, dy) != (0, 0):
            score += 1
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]]