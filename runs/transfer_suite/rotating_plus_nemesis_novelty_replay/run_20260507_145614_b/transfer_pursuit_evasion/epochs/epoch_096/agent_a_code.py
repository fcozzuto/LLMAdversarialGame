def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # opponent response: choose move that maximizes distance to us (deterministic tie-break by lexicographic)
        best_op = None
        best_op_val = None
        for edx, edy in moves:
            ex, ey = ox + edx, oy + edy
            if not inb(ex, ey) or (ex, ey) in obst:
                continue
            d = dist2(ex, ey, nx, ny)
            if best_op_val is None or d > best_op_val or (d == best_op_val and (ex, ey) > best_op):
                best_op_val = d
                best_op = (ex, ey)

        val = best_op_val if best_op is not None else dist2(ox, oy, nx, ny)
        if best_val is None or val < best_val or (val == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_val = val
            best_move = (dx, dy)

    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]