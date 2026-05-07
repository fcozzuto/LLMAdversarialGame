def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best_t = None
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer resources where we are earlier; otherwise block by maximizing opponent lead gap.
        # Key: (opp_lead, -my_dist, -my_pos_progress_to_target)
        key = (opd - myd, -myd, (tx - sx) * 0.0 + (ty - sy) * 0.0, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # If we're not already winning the target, don't help the opponent too much.
        score = (opd2 - myd2, -myd2)
        # Deterministic tie-breaker: prefer diagonal/forwardish moves earlier in list.
        tieb = (0 if (dx, dy) != (0, 0) else -1, 0)
        if best_score is None or score > best_score or (score == best_score and tieb > (0, 0)):
            best_score = score
            best_move = [dx, dy]

    return best_move