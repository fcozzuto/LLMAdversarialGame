def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource: prioritize closer-to-me and farther-from-opponent
    if resources:
        best = None
        for x, y in resources:
            d_my = md(sx, sy, x, y)
            d_opp = md(ox, oy, x, y)
            key = (d_my - d_opp, d_my, x, y)
            if best is None or key < best[0]:
                best = (key, x, y)
        tx, ty = best[1], best[2]
    else:
        tx, ty = w // 2, h // 2

    res_set = set((x, y) for x, y in resources)

    best_move = (0, 0)
    best_key = None
    # Deterministic move ordering for tie-break
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        onto_res = 1 if (nx, ny) in res_set else 0

        # Prefer collecting immediately, then reducing distance to target,
        # and (secondarily) increase opponent disadvantage at target.
        key = (
            -onto_res,
            my_d,
            (md(sx, sy, tx, ty) - my_d),  # prefer progress
            (my_d - opp_d),              # keep target relatively worse for opponent
            dx, dy
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]