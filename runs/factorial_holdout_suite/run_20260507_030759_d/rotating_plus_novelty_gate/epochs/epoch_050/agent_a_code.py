def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources_list = observation.get("resources", []) or []
    resources = [tuple(r) for r in resources_list]

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if (sx, sy) in set(resources):
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            self_d = manh(nx, ny, ox, oy)
            cand = (-self_d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    best = None
    res_set = set(resources)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            return [dx, dy]
        best_for_cell = None
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Prefer resources where we can arrive earlier than opponent; also prefer being close.
            # Deterministic tie-breaking by dx,dy.
            val = (od - sd, -sd, -manh(nx, ny, ox, oy))
            if best_for_cell is None or val > best_for_cell:
                best_for_cell = val
        cand = (best_for_cell[0], best_for_cell[1], best_for_cell[2], -dx, -dy, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[5], best[6]]