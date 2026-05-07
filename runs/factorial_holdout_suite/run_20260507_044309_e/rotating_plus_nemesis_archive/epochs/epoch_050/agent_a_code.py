def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def dist_cheb(x, y, tx, ty):
        dx = x - tx
        if dx < 0:
            dx = -dx
        dy = y - ty
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prefer the resource we can reach sooner than opponent; tie-break by position.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = dist_cheb(sx, sy, rx, ry)
        do = dist_cheb(ox, oy, rx, ry)
        key = (ds > do, ds, abs(rx - sx) + abs(ry - sy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = tx - sx
    dy = ty - sy
    if dx > 0:
        step_x = 1
    elif dx < 0:
        step_x = -1
    else:
        step_x = 0
    if dy > 0:
        step_y = 1
    elif dy < 0:
        step_y = -1
    else:
        step_y = 0

    candidates = []
    candidates.append((step_x, step_y))
    if step_x != 0 and step_y != 0:
        candidates.append((step_x, 0))
        candidates.append((0, step_y))
    candidates.append((0, 0))

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]

    # Deterministic fallback if blocked: scan a fixed order.
    for mx, my in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]
    return [0, 0]