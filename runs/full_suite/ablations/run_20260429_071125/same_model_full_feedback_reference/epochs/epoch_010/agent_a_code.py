def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_us = None
    best_us_key = None
    best_op = None
    best_op_key = None

    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        us_key = (od - sd, -sd, rx, ry)          # maximize being closer than opponent
        op_key = (sd - od, -od, rx, ry)          # opponent wants maximize (their closeness) => ours disadvantage
        if best_us_key is None or us_key > best_us_key:
            best_us_key, best_us = us_key, (rx, ry)
        if best_op_key is None or op_key > best_op_key:
            best_op_key, best_op = op_key, (rx, ry)

    # If opponent is significantly closer to something than we are, contest that target.
    if best_us_key[0] < best_op_key[0]:
        tx, ty = best_op
    else:
        tx, ty = best_us

    dx = tx - sx
    dy = ty - sy
    stepdx = 0 if dx == 0 else (1 if dx > 0 else -1)
    stepdy = 0 if dy == 0 else (1 if dy > 0 else -1)

    candidates = [
        (stepdx, stepdy),
        (stepdx, 0),
        (0, stepdy),
        (stepdx, -stepdy),
        (-stepdx, stepdy),
        (0, 0),
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (-1, -1), (1, -1), (-1, 1),
    ]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [int(mx), int(my)]
    return [0, 0]