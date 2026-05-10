def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def to_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    unclaimed = to_set(observation.get("unclaimed_cells"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    if unclaimed:
        # Deny: aim for the unclaimed cell closest to opponent; tie-break by closeness to us.
        best_cell = None
        best_key = None
        for x, y in unclaimed:
            d_opp = abs(x - ox) + abs(y - oy)
            d_us = abs(x - sx) + abs(y - sy)
            key = (d_opp, d_us, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best_cell = (x, y)
        target = best_cell

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        cell_score = 0
        if (nx, ny) in oppT:
            cell_score += 12
        elif (nx, ny) in unclaimed:
            cell_score += 7
        elif (nx, ny) in selfT:
            cell_score += 2

        if target is None:
            # Expand generally toward center while not touching obstacles.
            dc = abs((nx - (w - 1) / 2.0)) + abs((ny - (h - 1) / 2.0))
            dist_term = -dc
        else:
            dist_term = - (abs(nx - target[0]) + abs(ny - target[1]))

        score = cell_score * 10 + dist_term

        key = (-(score), dx, dy)  # deterministic tie-break
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]