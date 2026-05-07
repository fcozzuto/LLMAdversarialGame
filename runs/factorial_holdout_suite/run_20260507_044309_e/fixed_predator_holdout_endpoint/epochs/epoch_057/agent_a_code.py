def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in (observation.get("obstacles", None) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inside(px, py):
                blocked.add((px, py))

    resources = []
    for r in (observation.get("resources", None) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry) and (rx, ry) not in blocked:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_cell = None
    best_val = None
    for cell in resources:
        cx, cy = cell
        sd = md(sx, sy, cx, cy)
        od = md(ox, oy, cx, cy)
        val = (od - sd, -sd, -cx, -cy)
        if best_val is None or val > best_val:
            best_val = val
            best_cell = cell

    tx, ty = best_cell

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in blocked:
                moves.append((dx, dy))
    moves.append((0, 0))

    cur_d = md(sx, sy, tx, ty)
    best_move = (0, 0)
    best_mv_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d2 = md(nx, ny, tx, ty)
        # If we can reduce our distance, do it; also avoid giving opponent a big tempo edge.
        nd_self = d2
        nd_opp = md(ox, oy, tx, ty)
        val = (-abs(d2 - d2), 0)  # placeholder removed by next assignment
        val = (-(d2), -(abs(d2 - cur_d)), -(md(ox, oy, tx, ty)), -nx, -ny)
        if best_mv_val is None or val > best_mv_val:
            best_mv_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]