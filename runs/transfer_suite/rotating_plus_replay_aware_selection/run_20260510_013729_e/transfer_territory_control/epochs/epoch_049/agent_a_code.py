def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    xo, yo = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    # Pick a deterministic target among nearby unclaimed cells
    un_list = list(unclaimed)
    if not un_list:
        # Fallback: expand toward center if nothing unclaimed
        target = ((w - 1) // 2, (h - 1) // 2)
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        # Choose cell that is best by (distance to center, distance from our pos)
        best = None
        best_key = None
        for ux, uy in un_list:
            if (ux, uy) in obstacles:
                continue
            key = (abs(ux - cx) + abs(uy - cy), abs(ux - xp) + abs(uy - yp), ux, uy)
            if best_key is None or key < best_key:
                best_key = key
                best = (ux, uy)
        target = best if best is not None else (un_list[0][0], un_list[0][1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    myc = int(observation.get("self_territory_count") or len(myt))
    optc = int(observation.get("opponent_territory_count") or len(opt))
    we_are_small = myc < optc

    for dx, dy in moves:
        nx, ny = xp + dx, yp + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 35.0
        if (nx, ny) in myt:
            score += 6.0
        if (nx, ny) in opt:
            score -= 22.0 if we_are_small else 16.0

        # Progress toward target (and away from opponent if we're not leading)
        score += -0.9 * (abs(nx - target[0]) + abs(ny - target[1]))
        score += 0.15 * (abs(xo - nx) + abs(yo - ny))
        # Mild center preference to avoid edge traps
        centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.05 * (abs(nx - centerx) + abs(ny - centery))

        # Deterministic tie-break: prefer smaller dx, then dy, then staying
        tie = (0 if (dx == 0 and dy == 0) else 1, dx, dy)
        final = (score, -tie[0], -tie[1], -tie[2])

        if best_score is None or final > best_score:
            best_score = final
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]