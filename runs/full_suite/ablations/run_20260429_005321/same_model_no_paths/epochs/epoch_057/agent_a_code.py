def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manhattan(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    target = min(resources, key=lambda t: (manhattan(sx, sy, t[0], t[1]), t[0], t[1]))
    tx, ty = target

    moves = [(0, -1), (-1, 0), (0, 0), (1, 0), (0, 1)]
    best = None
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = manhattan(nx, ny, tx, ty)
            if bestd is None or d < bestd or (d == bestd and (nx, ny) < best):
                bestd = d
                best = (nx, ny)

    if best is None:
        return [0, 0]
    return [best[0] - sx, best[1] - sy]