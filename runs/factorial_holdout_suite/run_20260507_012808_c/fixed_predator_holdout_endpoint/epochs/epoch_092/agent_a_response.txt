def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def md(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    # Prefer resources we can reach earlier than opponent (deny), else challenge opponent's closest resource.
    best = None
    for t in resources:
        sd = md(t[0], t[1], sx, sy)
        od = md(t[0], t[1], ox, oy)
        if od - sd >= 0:
            cand = (2, od - sd, -sd, t)
        else:
            cand = (1, -od, sd, t)
        if best is None or cand > best:
            best = cand
    target = best[3]
    tx, ty = int(target[0]), int(target[1])

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    options = [(dx, dy)]
    options.append((dx, 0))
    options.append((0, dy))
    options.append((-dx, dy))
    options.append((dx, -dy))
    options.append((0, 0))

    for a, b in options:
        nx, ny = sx + a, sy + b
        if valid(nx, ny):
            return [int(a), int(b)]
    return [0, 0]