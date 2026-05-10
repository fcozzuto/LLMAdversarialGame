def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def to_set(val):
        s = set()
        for p in val or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    unclaimed = to_set(observation.get("unclaimed_cells"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opponent_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opponent_pos[0]), int(opponent_pos[1])

    un_list = list(unclaimed)
    if not un_list:
        un_list = None

    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        cell = (nx, ny)
        # Territory preference: unclaimed > steal opponent > stay/neutral
        if cell in unclaimed:
            base = 1000
        elif cell in oppT:
            base = 450
        elif cell in selfT:
            base = 80
        else:
            base = 40

        # Move toward the best target deterministically
        if un_list is not None:
            # nearest unclaimed from this move
            tx, ty = min(un_list, key=lambda c: (abs(c[0] - nx) + abs(c[1] - ny), c[0], c[1]))
            dist_un = abs(tx - nx) + abs(ty - ny)
        else:
            dist_un = 999

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)

        # If unclaimed exists, heavily prefer reducing distance to it.
        # Otherwise, prefer stealing near opponent and advancing toward center.
        score = base - (10 * dist_un if un_list is not None else 0) - (2.5 * dist_center) + (0.6 * dist_opp * (-1))

        # Deterministic tie-break: lexicographic by (dx,dy)
        key = (-score, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]