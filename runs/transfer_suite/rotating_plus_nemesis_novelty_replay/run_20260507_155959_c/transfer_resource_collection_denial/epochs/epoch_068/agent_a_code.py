def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            s = (dist((nx, ny), (tx, ty)), abs(dx) + abs(dy), -nx, -ny)
            if best is None or s < best:
                best = s
                best_mv = (dx, dy)
        return [best_mv[0], best_mv[1]]

    best = None
    best_mv = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my_pos = (nx, ny)
        best_res_for_move = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                if not (0 <= rx < w and 0 <= ry < h):
                    continue
                oppd = dist((ox, oy), (rx, ry))
                myd = dist(my_pos, (rx, ry))
                # Prefer being closer than opponent; if not possible, reduce gap and myd.
                s = (myd - oppd, myd, -rx, -ry)
                if best_res_for_move is None or s < best_res_for_move:
                    best_res_for_move = s
        if best_res_for_move is None:
            continue
        if best is None or best_res_for_move < best:
            best = best_res_for_move
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]