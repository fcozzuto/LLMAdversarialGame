def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer closer to us; tie-break: larger lead over opponent (i.e., opponent farther)
            key = (sd, -(od - sd), tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        tx, ty = best[1]
    else:
        tx, ty = w // 2, h // 2

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen = set()
    for mx, my in moves:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]

    # Absolute fallback
    for mx, my in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]
    return [0, 0]