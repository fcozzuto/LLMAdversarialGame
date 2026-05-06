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

    def eval_pos(px, py):
        if not resources:
            return 0
        best = None
        for tx, ty in resources:
            d_me = abs(tx - px) + abs(ty - py)
            d_opp = abs(tx - ox) + abs(ty - oy)
            lead = d_opp - d_me
            tv = lead * 1000 - d_me + 0.01 * d_opp
            if best is None or tv > best[0] or (tv == best[0] and (d_me < best[1] or (d_me == best[1] and (tx, ty) < best[2]))):
                best = (tv, d_me, (tx, ty))
        return best[0]

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and not blocked(nx, ny):
            v = eval_pos(nx, ny)
        else:
            v = -10**18  # invalid, but engine will keep us in place; we avoid it deterministically

        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    # Fallback if all moves invalid (should be rare)
    if best_val is None or best_val <= -10**17:
        return [0, 0]
    return [best_move[0], best_move[1]]