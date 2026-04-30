def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    my_moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Pick target resource with best relative advantage (I am closer).
    if resources:
        best = None
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            myd = abs(rx - sx) + abs(ry - sy)
            opd = abs(rx - ox) + abs(ry - oy)
            score = (myd - opd, myd)  # smaller is better
            if best is None or score < best[0]:
                best = (score, (rx, ry), myd, opd)
        tx, ty = best[1]
    else:
        tx, ty = (w // 2, h // 2)
    # Evaluate each legal move.
    best_move = (0, 0)
    best_val = None
    for dx, dy in my_moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary: move closer to target; Secondary: keep away from opponent; Tertiary: keep stable.
        dist_t = abs(tx - nx) + abs(ty - ny)
        dist_o = abs(ox - nx) + abs(oy - ny)
        # Slightly prefer moves that increase distance from opponent when contesting.
        contest_bias = 0
        if resources:
            myd = abs(tx - sx) + abs(ty - sy)
            opd = abs(tx - ox) + abs(ty - oy)
            if myd > opd:
                contest_bias = -1  # I'm behind at chosen target; run.
        val = (dist_t, -dist_o, -abs(dx) - abs(dy), contest_bias)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]