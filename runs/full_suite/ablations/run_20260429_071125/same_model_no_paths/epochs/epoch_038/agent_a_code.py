def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    candidates = []
    if resources:
        # Target the closest resource, but move choices also consider opponent distance.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            dop = cheb(nx, ny, ox, oy)
            # If a move lands on a resource, heavily prioritize it.
            hit = 0 if (nx, ny) in resources else 1
            score = (dres * 12) - (dop * 2) + hit * 0.5 + (dx * dx + dy * dy) * 0.1
            candidates.append((score, hit, dres, -dop, dx, dy))
        candidates.sort()
        return [int(candidates[0][4]), int(candidates[0][5])]
    else:
        # No visible resources: maximize safety from opponent and drift toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dop = cheb(nx, ny, ox, oy)
            dc = abs(nx - cx) + abs(ny - cy)
            score = (-dop * 10) + dc + (dx * dx + dy * dy) * 0.05
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]
        return [int(best[0]), int(best[1])]