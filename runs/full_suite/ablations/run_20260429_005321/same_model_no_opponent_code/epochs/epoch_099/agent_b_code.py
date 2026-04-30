def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_to(tx, ty, nx, ny):
        dres = abs(nx - tx) + abs(ny - ty)
        dop = max(0, 999999 - (abs(nx - ox) + abs(ny - oy)))
        return dres, -dop

    best_move = (0, 0)
    best_val = None

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            best_res = None
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if best_res is None or d < best_res:
                    best_res = d
            # Prefer closer to any resource; tie-break away from opponent; deterministic order already helps
            val = (best_res, abs(nx - ox) + abs(ny - oy))
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No resources: move to maximize distance from opponent while staying valid
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            # Small tie-break toward increasing x then y deterministically
            val = (-d, -nx, -ny)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]