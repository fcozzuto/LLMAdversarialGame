def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    sc = observation.get("scores") or {}
    try:
        my_score = float(sc.get("self", sc.get(0, 0)))
        opp_score = float(sc.get("opponent", sc.get(1, 0)))
    except Exception:
        my_score, opp_score = 0.0, 0.0

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    if resources:
        tx, ty = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    else:
        tx, ty = ox, oy

    behind = my_score < opp_score
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if behind:
            val = -man(nx, ny, tx, ty) + 0.1 * man(nx, ny, ox, oy)
        else:
            val = man(nx, ny, ox, oy) - 0.1 * man(nx, ny, tx, ty)
        if best is None or val > best_val:
            best, best_val = [dx, dy], val

    if best is None:
        return [0, 0]
    return best