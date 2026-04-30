def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = resources[0]
    best_val = -(10**18)
    for tx, ty in resources:
        d_own = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        val = -(d_own) + 0.35 * (d_op - d_own)  # prefer resources we are closer to, discourage shared races
        # tie-break deterministically by coordinates
        if val > best_val or (val == best_val and (tx, ty) < best_target):
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target
    cenx, ceny = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -(10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_now = cheb(sx, sy, tx, ty)
        d_new = cheb(nx, ny, tx, ty)
        opp_dist_now = cheb(ox, oy, tx, ty)
        opp_dist_new = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        # primary: reduce distance to target; secondary: slightly avoid letting opponent also be closer
        score = (d_now - d_new) * 5.0
        score += 0.10 * cheb(nx, ny, cenx, ceny) * (-1)  # prefer moving toward center (use negative cheb so smaller better)
        score += -0.15 * cheb(nx, ny, ox, oy)  # keep some spacing from opponent
        # deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]