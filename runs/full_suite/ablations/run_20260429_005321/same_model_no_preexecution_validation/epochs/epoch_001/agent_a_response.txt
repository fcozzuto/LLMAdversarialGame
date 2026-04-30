def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] if observation["resources"] is not None else []
    obstacles = set(tuple(p) for p in (observation["obstacles"] if observation["obstacles"] is not None else []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # If no resources, head toward opponent slightly to reduce their options
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    best = None
    best_score = -10**18
    for rx, ry in resources:
        # Prefer closer resources, and especially those where we are not slower than opponent.
        md_s = abs(rx - sx) + abs(ry - sy)
        md_o = abs(rx - ox) + abs(ry - oy)
        # Deterministic tiebreaker by coordinates.
        score = (10000 if md_s < md_o else 0) - md_s + (0.001 * (-rx) + 0.0001 * (-ry)) - 0.5 * md_o
        if best is None or score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # Evaluate all possible moves and choose best feasible one
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_m = (0, 0)
    best_m_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Move score: decrease distance to target, also avoid allowing opponent to become closer next
        d_now = abs(tx - sx) + abs(ty - sy)
        d_next = abs(tx - nx) + abs(ty - ny)
        d_opp_next = abs(tx - ox) + abs(ty - oy)
        # Prefer breaking ties deterministically: favor smaller dx then dy.
        score = (d_now - d_next) * 10 + (d_opp_next - (d_opp_next)) * 0
        score += -0.001 * (abs(nx - tx) + abs(ny - ty))
        score += -0.00001 * (dx * 10 + dy)
        if score > best_m_score:
            best_m_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]