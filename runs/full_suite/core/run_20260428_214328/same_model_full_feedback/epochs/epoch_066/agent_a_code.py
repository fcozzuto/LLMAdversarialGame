def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w = 8
        h = 8

    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx = int(sp[0]) if isinstance(sp, (list, tuple)) and len(sp) > 0 else 0
    sy = int(sp[1]) if isinstance(sp, (list, tuple)) and len(sp) > 1 else 0
    ox = int(op[0]) if isinstance(op, (list, tuple)) and len(op) > 0 else 0
    oy = int(op[1]) if isinstance(op, (list, tuple)) and len(op) > 1 else 0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0])
            y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0])
            y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem)
    except:
        rem = 0
    late = rem <= 4

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    bestv = None

    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not ok(nx, ny):
            continue
        if resources and not late:
            bestres = None
            bestscore = None
            for rx, ry in resources:
                ds = adist(nx, ny, rx, ry)
                dop = adist(ox, oy, rx, ry)
                # Prefer minimizing our distance; avoid giving opponent an advantage.
                s = ds * 10 + (0 if ds <= dop else 3 * (ds - dop))
                if bestscore is None or s < bestscore:
                    bestscore = s
                    bestres = (rx, ry)
            v = bestscore if bestscore is not None else adist(nx, ny, ox, oy)
        else:
            # Late: head toward opponent (or stay if blocked).
            v = adist(nx, ny, ox, oy)

        if bestv is None or v < bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx = sx + dx
            ny = sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]