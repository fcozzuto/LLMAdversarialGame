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

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        # Deterministic fallback: move toward center-left relative to opponent
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def best_score_from(px, py):
        best = -10**18
        for tx, ty in resources:
            if blocked(tx, ty):
                continue
            d_me = abs(tx - px) + abs(ty - py)
            d_opp = abs(tx - ox) + abs(ty - oy)
            # Strongly prefer resources where we are closer than opponent, then closer generally
            s = (d_opp - d_me) * 1000 - d_me + 0.01 * d_opp
            if s > best:
                best = s
        return best

    # Aim to reduce opponent advantage: choose move maximizing best_score from next position
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        val = best_score_from(nx, ny)
        # Small deterministic bias toward moving (avoid stalling when equal)
        if dx == 0 and dy == 0:
            val -= 0.25
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]