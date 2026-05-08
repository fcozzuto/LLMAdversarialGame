def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((sx == r[0] and sy == r[1]) for r in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best_target = None
    best_priority = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; tie-break by closer distance and stable ordering
        reachable_bonus = 6 if d_me <= d_op else 0
        priority = reachable_bonus * 100 - d_me * 3 - d_op
        if d_me == 0:
            priority = 10**9
        if priority > best_priority:
            best_priority = priority
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_score = -10**18

    # Small deterministic "avoid being trapped by denier": prefer moves that reduce distance to target
    # and don't step closer to opponent unless it helps reach target.
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        d_new = cheb(nx, ny, rx, ry)
        d_op_new = cheb(nx, ny, ox, oy)

        d_me_old = cheb(sx, sy, rx, ry)
        d_op_old = cheb(ox, oy, rx, ry)

        # Estimate whether we are racing this resource
        new_race_win = 1 if d_new <= d_op_old else 0
        race_term = new_race_win * 120 - d_new * 6

        # Opponent-denial pressure: avoid moving adjacent unless we are winning the race
        opp_term = (d_op_new) * (2 if new_race_win else 5) - (0 if new_race_win else 6)

        # Prefer not to wander: reduce distance monotonically when possible
        progress = (d_me_old - d_new) * 10

        score = race_term + opp_term + progress
        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]