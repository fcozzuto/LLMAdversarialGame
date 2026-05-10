def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opt = to_set("opponent_territory")

    cx, cy = (w - 1) // 2, (h - 1) // 2

    candidates = list(unclaimed) if unclaimed else list(opt)
    if not candidates:
        # Last resort: drift toward center while avoiding obstacles
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = (10**9, [0, 0])
        for dx, dy in moves:
            nx, ny = xp + dx, yp + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = abs(nx - cx) + abs(ny - cy)
            if d < best[0]:
                best = (d, [dx, dy])
        return best[1]

    # Deterministic tie-breaking: prefer nearer to center, then nearer to us
    # Also slightly prefer targets closer to our side of the map (to keep pushing outward)
    best = None
    best_key = None
    for tx, ty in candidates:
        if (tx, ty) in obstacles:
            continue
        d_us = abs(tx - xp) + abs(ty - yp)
        d_center = abs(tx - cx) + abs(ty - cy)
        edge_bias = (tx < cx and xp < cx) or (tx > cx and xp > cx)
        # When unclaimed exists, prioritize capturing it; else push into opponent territory.
        flip_bias = 0
        if unclaimed:
            flip_bias = 0
        else:
            # Bias toward entering opponent territory that is closer to their "front"
            # (cells closer to our position generally yield faster flips).
            flip_bias = 1
        key = (d_us, d_center, 0 if edge_bias else 1, flip_bias, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == xp else (1 if tx > xp else -1)
    dy = 0 if ty == yp else (1 if ty > yp else -1)

    # If direct diagonal/straight step hits obstacle, choose best neighbor that reduces heuristic.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def score(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return 10**9
        d = abs(tx - nx) + abs(ty - ny)
        # Encourage moving toward center and away from opponent if we are already close
        dc = abs(nx - cx) + abs(ny - cy)
        return d + 0.03 * dc

    best_move = None
    best_val = None
    for mdx, mdy in moves:
        nx, ny = xp + mdx, yp + mdy
        val = score(nx, ny)
        if best_val is None or val < best_val or (val == best_val and (mdx, mdy) < best_move):
            best_val = val
            best_move = [mdx, mdy]

    return best_move