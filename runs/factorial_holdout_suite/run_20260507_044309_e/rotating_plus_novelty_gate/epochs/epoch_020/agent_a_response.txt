def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = [(x, y) for (x, y) in resources if inb(x, y)]
    if not valid:
        return [0, 0]

    # Prefer moves that reduce our capture time relative to opponent.
    best = (0, 0); best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate this next cell against all resources.
        cur_best = -10**18
        for rx, ry in valid:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # If we can reach now (or next step) and deny theirs, huge reward.
            if sd == 0:
                score = 10**12
            else:
                score = (od - sd) * 10**6

            # Tie-break: prefer closer resources overall, and prefer taking lines aligned with opponent.
            score -= sd * 3
            if ry == oy or rx == ox:
                score += 50
            # Avoid moving into squares that are very close to opponent (denial games).
            score -= max(0, 4 - man(nx, ny, ox, oy)) * 40

            if score > cur_best:
                cur_best = score

        if cur_best > best_score:
            best_score = cur_best
            best = (dx, dy)

    return [int(best[0]), int(best[1])]