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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_for_target(tx, ty, step_nx, step_ny):
        return (tx - step_nx) * (tx - step_nx) + (ty - step_ny) * (ty - step_ny)

    best = None
    best_score = None

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = None
            for rx, ry in resources:
                d = best_for_target(rx, ry, nx, ny)
                if score is None or d < score:
                    score = d
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
            elif score == best_score:
                if (dx, dy) < best:
                    best = (dx, dy)
        if best is not None:
            return [int(best[0]), int(best[1])]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if best_score is None or d > best_score:
            best_score = d
            best = (dx, dy)
        elif d == best_score:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]