def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    res = observation.get("resources") or []
    rpos = []
    for p in res:
        if isinstance(p, dict):
            x = p.get("x", p.get("pos_x", p.get("position_x", None)))
            y = p.get("y", p.get("pos_y", p.get("position_y", None)))
            if x is not None and y is not None:
                x, y = int(x), int(y)
                if 0 <= x < w and 0 <= y < h:
                    rpos.append((x, y))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rpos.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        # primary: go toward nearest resource if any; otherwise chase opponent
        if rpos:
            dres = min(abs(nx - rx) + abs(ny - ry) for (rx, ry) in rpos)
            target_score = 1000000 - dres
        else:
            dres = abs(nx - ox) + abs(ny - oy)
            target_score = 1000000 - dres

        # secondary: if close to opponent, prefer moving onto them
        onto_opp = 1 if (nx, ny) == (ox, oy) else 0

        key = (onto_opp, target_score, -abs(nx - sx) - abs(ny - sy), 0, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]