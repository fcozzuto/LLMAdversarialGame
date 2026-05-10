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

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # If we have territory, move toward its outward frontier (estimated by nearest unclaimed)
    my_list = list(myt) if myt else []
    base = my_list[0] if my_list else (xp, yp)

    candidates = list(unclaimed) if unclaimed else []
    if not candidates:
        # Fallback: head toward center while staying away from opponent
        tx, ty = cx, cy
        if abs(tx - xp) + abs(ty - yp) == 0:
            # If already at center, move directly away from opponent
            dx = 0 if xp == xo else (1 if xp > xo else -1)
            dy = 0 if yp == yo else (1 if yp > yo else -1)
            return [dx, dy]
    else:
        # Score candidates: prefer near frontier, near center, far from opponent, and not on obstacles
        best = None
        best_key = None
        for ux, uy in candidates:
            if (ux, uy) in obstacles:
                continue
            d_front = abs(ux - base[0]) + abs(uy - base[1])
            d_op = abs(ux - xo) + abs(uy - yo)
            d_ctr = abs(ux - cx) + abs(uy - cy)
            # Slightly prefer cells likely to flip enemy less: avoid stepping into opponent territory immediately
            on_enemy = 1 if (ux, uy) in opt else 0
            # Deterministic lexicographic key
            key = (on_enemy, d_front, d_ctr, -d_op, ux, uy)
            if best_key is None or key < best_key:
                best_key = key
                best = (ux, uy)
        tx, ty = best if best is not None else (cx, cy)

    # Choose a deterministic step toward target; if tie, prioritize staying/advancing in axis toward target.
    dx = 0 if tx == xp else (1 if tx > xp else -1)
    dy = 0 if ty == yp else (1 if ty > yp else -1)

    # If moving diagonally would land on obstacle, try axis move (still deterministic)
    nx, ny = xp + dx, yp + dy
    if dx != 0 and dy != 0 and (nx, ny) in obstacles:
        # Prefer axis that reduces Manhattan distance more
        adx = 0 if tx == xp else (1 if tx > xp else -1)
        ady = 0 if ty == yp else (1 if ty > yp else -1)
        ax1 = (xp + adx, yp)
        ax2 = (xp, yp + ady)
        d1 = abs(tx - ax1[0]) + abs(ty - ax1[1])
        d2 = abs(tx - ax2[0]) + abs(ty - ax2[1])
        if (ax1[0], ax1[1]) in obstacles and (ax2[0], ax2[1]) in obstacles:
            return [0, 0]
        if (ax1[0], ax1[1]) in obstacles:
            return [0, ady]
        if (ax2[0], ax2[1]) in obstacles:
            return [adx, 0]
        if d1 < d2:
            return [adx, 0]
        if d2 < d1:
            return [0, ady]
        return [adx if adx != 0 else 0, 0 if adx != 0 else ady]

    return [dx, dy]