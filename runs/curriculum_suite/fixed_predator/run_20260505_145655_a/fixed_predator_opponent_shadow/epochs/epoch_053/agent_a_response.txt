def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        dx = sign(x - ox)
        dy = sign(y - oy)
        if dx == 0 and dy == 0:
            return [0, 0]
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target_value(px, py):
        best = None
        for tx, ty in resources:
            d_me = man(px, py, tx, ty)
            d_opp = man(ox, oy, tx, ty)
            # Prefer cells where we are relatively closer than opponent, then closer overall
            lead = d_opp - d_me
            tv = lead * 1000 - d_me - 0.001 * d_opp
            if best is None or tv > best[0] or (tv == best[0] and (tx, ty) < (best[1], best[2])):
                best = (tv, tx, ty)
        return best

    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            continue
        bt = best_target_value(nx, ny)
        tv, tx, ty = bt
        d_me = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Small bias to not step away from the current best target
        current_best = best_target_value(x, y)
        cur_tv, cur_tx, cur_ty = current_best
        step_toward = (man(x, y, cur_tx, cur_ty) - d_me)
        safety = -0.1 * man(nx, ny, ox, oy)
        score = tv + step_toward + safety
        if (best_score is None or score > best_score or
            (score == best_score and (nx, ny) < best_move) ):
            best_score = score
            best_move = (nx, ny)

    if best_move is None:
        # All moves blocked or out of bounds: stay
        return [0, 0]
    return [best_move[0] - x, best_move[1] - y]