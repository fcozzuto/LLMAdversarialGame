def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def best_target_value(px, py):
        if not resources:
            return -10**18
        best = None
        bestv = -10**18
        for tx, ty in resources:
            d_me = abs(tx - px) + abs(ty - py)
            d_opp = abs(tx - ox) + abs(ty - oy)
            lead = d_opp - d_me
            v = lead * 1000 - d_me + 0.01 * d_opp
            if best is None or v > bestv or (v == bestv and (d_me < best[0] or (d_me == best[0] and (tx, ty) < best[1]))):
                best = (d_me, (tx, ty))
                bestv = v
        return bestv

    if not resources:
        nx = x + (-sign(ox - x))
        ny = y + (-sign(oy - y))
        if in_bounds(nx, ny) and not blocked(nx, ny):
            return [-sign(ox - x), -sign(oy - y)]
        return [sign(ox - x), sign(oy - y)]

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        move_block_pen = 0
        if blocked(nx, ny):
            move_block_pen = 10**6
        v = best_target_value(nx, ny)
        # Encourage moving to positions where we can arrive sooner than opponent, penalize stagnant moves slightly
        dist_self = abs(nx - x) + abs(ny - y)
        v2 = v - move_block_pen + 0.2 * dist_self
        # Deterministic tie-break
        if v2 > best_score or (v2 == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = v2
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]