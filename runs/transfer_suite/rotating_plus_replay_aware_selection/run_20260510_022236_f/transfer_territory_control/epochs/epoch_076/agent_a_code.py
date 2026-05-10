def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    my_score = int((observation.get("scores") or {}).get("self") or 0)
    opp_score = int((observation.get("scores") or {}).get("opponent") or 0)
    behind = my_score <= opp_score

    def pick_target(cands):
        tx, ty = cx, cy
        best = 10**18
        for p in cands:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
                    if d < best:
                        best = d
                        tx, ty = x, y
        return tx, ty

    target = pick_target(unclaimed if unclaimed else resources if resources else [])
    tx, ty = float(target[0]) if isinstance(target, (list, tuple)) else float(target[0]), float(target[1]) if isinstance(target, (list, tuple)) else float(target[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d_o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        val = -d_t
        if behind:
            val += 0.4 * d_o  # when behind, avoid opponent
        else:
            val += -0.15 * d_o  # when ahead, move closer to opponent

        if (nx, ny) in (set(tuple(p[:2]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2) if unclaimed else set()):
            val += 1e9
        if (nx, ny) in (set(tuple(p[:2]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2) if resources else set()):
            val += 5e5

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]