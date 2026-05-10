def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = str(observation.get("self_role") or "").lower()
    evader = "evader" in role

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if resources:
            d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            val = d
            want = "min"
        else:
            d = abs(nx - ox) + abs(ny - oy)
            val = -d if evader else d
            want = "max"

        if best_val is None:
            best_val, best = val, (dx, dy)
        else:
            if want == "min":
                if val < best_val:
                    best_val, best = val, (dx, dy)
            else:
                if val > best_val:
                    best_val, best = val, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]