def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obs_cells = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_cells.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target: minimize our distance, but prefer targets where we are relatively closer than opponent.
    best_t = resources[0]
    best_score = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        score = myd - 0.35 * opd
        if best_score is None or score < best_score or (score == best_score and (rx, ry) < (best_t[0], best_t[1])):
            best_score = score
            best_t = [rx, ry]

    tx, ty = best_t[0], best_t[1]
    res_set = set((int(r[0]), int(r[1])) for r in resources)

    moves = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_cells:
            continue
        d = cheb(nx, ny, tx, ty)
        on_res = 1 if (nx, ny) in res_set else 0
        # If we can grab now, do it; otherwise head toward target and lightly keep from aiding opponent.
        val = (-1000 if on_res else 0) + d
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]