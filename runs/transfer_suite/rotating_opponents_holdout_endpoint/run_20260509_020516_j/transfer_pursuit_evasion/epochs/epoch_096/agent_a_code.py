def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def clamp_in(x, y):
        x = 0 if x < 0 else (w - 1 if x >= w else x)
        y = 0 if y < 0 else (h - 1 if y >= h else y)
        return x, y

    if (sx, sy) in obstacles:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = clamp_in(sx + dx, sy + dy)
            if (nx, ny) not in obstacles:
                sx, sy = nx, ny
                break

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Slightly bias toward avoiding obstacles and toward useful corners/lines
    corner_bias = 0
    if sx <= 1:
        corner_bias += 1
    if sx >= w - 2:
        corner_bias += 1
    if sy <= 1:
        corner_bias += 1
    if sy >= h - 2:
        corner_bias += 1

    for dx, dy in moves:
        nx, ny = clamp_in(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # obstacle proximity penalty: prefer staying away from obstacle-adjacent tiles for evader,
        # and for pursuer prefer tiles that are not "blocked-crowded".
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    prox += 1

        if is_evader:
            # maximize distance; minimize obstacle proximity; slight prefer increasing x+y when far from opponent
            val = (dist * 1000) - (prox * 10) + (1 if (nx + ny) > (sx + sy) else 0) * corner_bias
        else:
            # minimize distance; minimize obstacle proximity; slight prefer moving toward opponent corner region
            val = (-dist * 1000) - (prox * 10) - (1 if (nx + ny) < (sx + sy) else 0) * corner_bias

        # deterministic tie-breaker by lexicographic (dx,dy)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]