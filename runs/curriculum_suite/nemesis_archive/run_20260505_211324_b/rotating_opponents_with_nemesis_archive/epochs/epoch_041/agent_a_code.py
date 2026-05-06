def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_best_adv(px, py):
        best_adv = -10**9
        best_res = None
        for tx, ty in res:
            myd = md(px, py, tx, ty)
            opd = md(ox, oy, tx, ty)
            adv = (opd - myd) * 5 - myd  # prefer winning races and closer picks
            # anticipate sweep_rows: resources on same row are more likely to be pressured
            if ty == py:
                adv -= 3
            if ty == oy:
                adv += 1  # deprioritize rows unlikely to matter? keep slight bias
            if adv > best_adv:
                best_adv = adv
                best_res = (tx, ty)
        return best_adv, best_res

    best_move = [0, 0]
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            adv, trg = cell_best_adv(nx, ny)
            # keep away from opponent sweeps: if we can be on/adjacent to opponent's row next, penalize
            row_pen = 0
            if ny == oy:
                row_pen += 8
            if abs(ny - oy) == 1:
                row_pen += 3
            # tie-break: prefer moves that reduce distance to the currently best target
            tie = 0
            if trg is not None:
                tie = -md(nx, ny, trg[0], trg[1]) + 0.2 * md(sx, sy, trg[0], trg[1])
            score = adv - row_pen + tie
            if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]

    return best_move