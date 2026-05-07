def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def neigh_obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        return [0, 0]

    best_t = None
    best_sc = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        # Prefer resources where we are earlier; also avoid those surrounded by obstacles slightly.
        sc = (od - sd) * 10 - sd - neigh_obst_pen(rx, ry)
        # Deterministic tie-break: prefer smaller sd then lexicographically smaller target.
        if best_t is None or sc > best_sc or (sc == best_sc and (sd < manh(sx, sy, best_t[0], best_t[1]) or
                                                                  (sd == manh(sx, sy, best_t[0], best_t[1]) and (rx, ry) < best_t))):
            best_t = (rx, ry)
            best_sc = sc

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = manh(nx, ny, tx, ty)
        od2 = manh(ox, oy, tx, ty)
        # Choose move that increases our race advantage; small tie-break on closer to target and fewer obstacle-adjacencies.
        val = (od2 - sd2) * 10 - sd2 - neigh_obst_pen(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer moves with smaller (abs(dx)+abs(dy)), then dx, then dy.
            cur_bd = abs(best_move[0]) + abs(best_move[1])
            new_bd = abs(dx) + abs(dy)
            if new_bd < cur_bd or (new_bd == cur_bd and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]