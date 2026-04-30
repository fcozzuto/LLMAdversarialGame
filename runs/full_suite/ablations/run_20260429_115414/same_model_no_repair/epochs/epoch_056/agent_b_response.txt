def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    p += 1
        return p

    def best_resource_for_pos(px, py):
        best = None
        for rx, ry in resources:
            sd = manh(px, py, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Prefer immediate pickup, then reduce opponent advantage; avoid targets too close to opponent if we can't beat them.
            key = (
                1000000 if sd == 0 else 0,
                (od - sd),
                -sd,
                -abs(rx - px) - abs(ry - py),
            )
            if best is None or key > best:
                best = key
        return best[0], best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        opp_dist_after = manh(ox, oy, nx, ny)
        self_dist_to_nearest = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        pickup_bonus, _ = best_resource_for_pos(nx, ny)

        # New approach: maximize (1) immediate pickup, (2) resource access relative to opponent, (3) safety/spacing from opponent,
        # while steering away from obstacle-adjacent cells.
        _, best_key = best_resource_for_pos(nx, ny)
        rel_adv = best_key[1] if best_key is not None else -1000
        score = (
            pickup_bonus +
            50 * rel_adv -
            3 * self_dist_to_nearest +
            0.8 * opp_dist_after -
            2.5 * obs_pen(nx, ny)
        )

        # Tie-break deterministically: prefer smaller dx, then smaller dy.
        tie = (-abs(dx), -abs(dy), -dx, -dy)
        score_tuple = (score, tie)
        if best_move[0] is None or score_tuple > best_move[1]:
            best_move = ([dx, dy], score_tuple)

    if best_move[0] is None:
        return [0, 0]
    return best_move[0]