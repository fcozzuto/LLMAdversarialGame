def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dist_to_opp = max(abs(nx - ox), abs(ny - oy))
        opp_pen = 0
        if dist_to_opp <= 2:
            opp_pen = (3 - dist_to_opp) * 100

        dist_to_res = 999999
        if resources:
            for rx, ry in resources:
                d = max(abs(nx - rx), abs(ny - ry))
                if d < dist_to_res:
                    dist_to_res = d

        res_gain = 0
        if resources and dist_to_res != 999999:
            res_gain = -dist_to_res * 10
        # slightly prefer advancing toward nearest resource direction deterministically
        toward = 0
        if resources:
            rx, ry = min(resources, key=lambda r: (max(abs(nx - r[0]), abs(ny - r[1])), r[0], r[1]))
            toward = -(abs(nx - rx) + abs(ny - ry))

        val = res_gain + toward - opp_pen + (0 if (dx, dy) != (0, 0) else 2)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]