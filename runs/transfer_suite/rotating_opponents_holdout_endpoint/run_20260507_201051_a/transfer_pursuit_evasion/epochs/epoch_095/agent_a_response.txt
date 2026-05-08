def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    role = (observation.get("self_role") or "").lower()
    pursuer = any(k in role for k in ("purs", "hunt", "chaser", "seeker", "hunter", "pursuer", "catch", "catcher"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    # If evader and near opponent, prioritize breaking diagonally away.
    near = dist2(sx, sy, ox, oy) <= 16

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        # obstacle proximity penalty (encourages paths that don't run into blocks)
        obst_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    obst_adj += 1
        # slight center preference to avoid getting boxed in
        center_pref = (3.5 - nx) * (3.5 - nx) + (3.5 - ny) * (3.5 - ny)

        if pursuer:
            # minimize distance; also discourage getting stuck against obstacles
            key = (d, obst_adj * 5 + center_pref * 0.01, abs((nx - ox)) + abs((ny - oy)))
        else:
            # maximize distance; avoid staying pressed against obstacles
            # if near, bias strong separation
            sep_bias = 1.35 if near else 1.0
            key = (-d * sep_bias, obst_adj * 5 + center_pref * 0.01, -(abs(nx - ox) + abs(ny - oy)))

        if best is None or key < best_key:
            best = (dx, dy)
            best_key = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]