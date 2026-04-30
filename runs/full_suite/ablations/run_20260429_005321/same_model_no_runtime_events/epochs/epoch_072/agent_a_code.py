def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    resources.sort()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev distance

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_resource_score(px, py):
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return md(px, py, cx, cy), md(ox, oy, cx, cy)
        best = None
        for rx, ry in resources:
            myd = md(px, py, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Prefer resources where we can arrive first; small center bias for tie stability
            key = (myd - opd, myd + (rx + ry) * 0.0001, rx, ry)
            if best is None or key < best[0]:
                best = (key, myd, opd)
        return best[1], best[2]

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd, opd = best_resource_score(nx, ny)
        # Prefer immediate pickup (resource on next cell) if possible
        pickup = 1 if (nx, ny) in obstacles else 0
        if pickup:
            continue
        on_resource = 1 if (nx, ny) in resources else 0
        # Also slightly avoid giving opponent a near-immediate advantage
        key = (-(on_resource), myd - opd, myd, md(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]