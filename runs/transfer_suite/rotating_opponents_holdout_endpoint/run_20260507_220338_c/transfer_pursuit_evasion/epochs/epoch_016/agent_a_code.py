def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources", []) or []
    res_pos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_pos.append((int(r[0]), int(r[1])))

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        dxo, dyo = nx - ox, ny - oy
        dist_op2 = dxo * dxo + dyo * dyo

        val = dist_op2  # prefer staying away from opponent
        if res_pos:
            best_res2 = None
            for rx, ry in res_pos:
                if (rx, ry) in blocked:
                    continue
                drx, dry = nx - rx, ny - ry
                d2 = drx * drx + dry * dry
                if best_res2 is None or d2 < best_res2:
                    best_res2 = d2
            if best_res2 is not None:
                val += 2000 // (1 + best_res2)  # prefer closer to resources

        # mild obstacle-proximity penalty
        if blocked:
            near = 0
            for bx, by in blocked:
                if abs(nx - bx) + abs(ny - by) <= 2:
                    near += 1
            val -= near * 3

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]