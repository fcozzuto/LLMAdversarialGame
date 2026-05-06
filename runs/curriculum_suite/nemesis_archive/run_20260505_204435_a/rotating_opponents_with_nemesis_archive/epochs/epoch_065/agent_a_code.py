def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles") or []:
        x = y = None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
        elif isinstance(p, dict):
            q = p.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = q[0], q[1]
        if x is not None and y is not None:
            x, y = int(x), int(y)
            if inb(x, y):
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x = y = None
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = q[0], q[1]
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        if x is not None and y is not None:
            x, y = int(x), int(y)
            if inb(x, y) and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    best = None
    best_score = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if d < best_score or (d == best_score and (dx, dy) < (best[0], best[1]) if best else True):
            best_score = d
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]