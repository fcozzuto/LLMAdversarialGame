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

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def is_valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        target = min(resources, key=lambda r: (dist(r[0], r[1], sx, sy), r[1], r[0]))
        tx, ty = target[0], target[1]
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not is_valid(nx, ny):
                continue
            score = (dist(nx, ny, tx, ty), dist(nx, ny, ox, oy) * 0)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        if best is not None:
            return [best[1], best[2]]
    else:
        tx, ty = ox, oy

        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not is_valid(nx, ny):
                continue
            score = dist(nx, ny, tx, ty)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        if best is not None:
            return [best[1], best[2]]

    return [0, 0]