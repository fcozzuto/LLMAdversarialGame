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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            # Prefer resources I'm relatively closer to than the opponent.
            best_val = None
            for rx, ry in resources:
                myd = man(nx, ny, sx, sy) * 0 + man(nx, ny, rx, ry)
                opd = man(nx, ny, rx, ry) - man(ox, oy, rx, ry)
                # Lower is better: my distance minus opponent advantage.
                val = myd - man(ox, oy, rx, ry) + 0
                if best_val is None or val < best_val:
                    best_val = val
            # Also mildly avoid getting too close to opponent.
            oppd = man(nx, ny, ox, oy)
            score = (best_val, -oppd)
        else:
            # No resources: move toward center and away from opponent.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dcenter = abs(nx - cx) + abs(ny - cy)
            oppd = man(nx, ny, ox, oy)
            score = (dcenter, -oppd)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]