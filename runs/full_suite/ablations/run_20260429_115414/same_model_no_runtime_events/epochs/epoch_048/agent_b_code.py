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

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem)
    except:
        rem = 0
    late = rem <= 3

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources and not late:
        tx, ty = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
        target = ("res", tx, ty)
    else:
        target = ("opp", ox, oy)

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target[0] == "res":
            dist = cheb(nx, ny, target[1], target[2])
            oppd = cheb(nx, ny, ox, oy)
            key = (dist, -oppd)  # closer to resource, and farther from opponent
        else:
            dist = cheb(nx, ny, target[1], target[2])
            oppd = cheb(nx, ny, ox, oy)
            key = (dist, -oppd)  # closer to opponent
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0] if valid(sx, sy) else next(([dx, dy] for dx, dy in dirs if valid(sx + dx, sy + dy)), [0, 0])