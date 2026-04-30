def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick target resource where we are relatively closer (try to "claim" before opponent).
    if resources:
        best = None
        for r in resources:
            d1 = dist((sx, sy), tuple(r))
            d2 = dist((ox, oy), tuple(r))
            # Prefer strong advantage; else still allow contesting but prefer lower own distance.
            score = (d2 - d1) * 10 - d1
            if best is None or score > best[0]:
                best = (score, tuple(r))
        target = best[1]
    else:
        target = (sx, sy)

    # If opponent is very close, reduce collision risk and prioritize escape toward target.
    opp_close = (dist((sx, sy), (ox, oy)) <= 2)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_target = abs(nx - target[0]) + abs(ny - target[1])
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        # Move value: get closer to target, keep distance from opponent, penalize stepping into tight areas.
        val = -d_to_target * 3 + d_to_opp
        if opp_close:
            val += d_to_opp * 2
        # Small deterministic tie-break: prefer staying/moving in x direction first, then y.
        val += (0.001 if (dx, dy) == (0, 0) else 0) + (0.0001 * (dx + 1)) + (0.00001 * (dy + 1))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]