def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources") or []
    if not res:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: beat opponent on distance AND avoid their likely sweep row.
    best = None
    best_key = None
    for r in res:
        tx, ty = int(r[0]), int(r[1])
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # sweep_rows heuristic: prefer resources with y far from opponent y
        row_gap = abs(ty - oy)
        key = (do - ds, row_gap, -ds, -do, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Choose best immediate move with obstacle avoidance.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obst:
            continue
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)  # opponent unchanged for this turn
        # maximize advantage and progress; also keep staying off opponent sweep row
        adv = (do2 - ds2)
        progress = -(ds2)
        row_pen = -abs(ty - oy)
        candidates.append((adv, progress, row_pen, -abs(nx - tx) - abs(ny - ty), dx, dy))

    if not candidates:
        # If blocked, allow obstacle cell (engine will keep us in place if invalid).
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            ds2 = md(nx, ny, tx, ty)
            do2 = md(ox, oy, tx, ty)
            adv = (do2 - ds2)
            progress = -(ds2)
            row_pen = -abs(ty - oy)
            candidates.append((adv, progress, row_pen, -abs(nx - tx) - abs(ny - ty), dx, dy))

    candidates.sort(reverse=True)
    return [int(candidates[0][4]), int(candidates[0][5])]