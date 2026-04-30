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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    tx, ty = sx, sy

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; then prefer closer overall.
            score = (do - ds, -ds)
            if best is None or score > best[0]:
                best = (score, rx, ry)
        _, tx, ty = best

    # If no resources, head to safer corner depending on remaining resources
    else:
        rem = observation.get("remaining_resource_count", 0)
        try:
            rem = int(rem)
        except:
            rem = 0
        if rem <= 4:
            tx, ty = 0, 0
        else:
            tx, ty = 0, h - 1

    # Choose step toward target; if blocked, try alternatives deterministically
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [
        (dx, dy),
        (dx, 0),
        (0, dy),
        (dx, -dy),
        (-dx, dy),
        (0, 0),
    ]
    # Ensure unique and deterministic
    seen = set()
    for m in moves:
        mx, my = m
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if valid(nx, ny):
            # If both dx and dy nonzero, slightly prefer diagonal when it improves distance to target
            return [mx, my]

    return [0, 0]