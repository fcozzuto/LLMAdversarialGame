def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)

    # One-step lookahead: maximize how many resources we can "reach first",
    # while strongly penalizing resources the opponent is closer to.
    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = 0
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # If we can collect immediately, dominate.
            if my_d == 0:
                val += 2000
                # If opponent is also at it, still count as our immediate priority.
                continue

            # Prefer resources where we are closer than opponent.
            gap = opp_d - my_d  # positive means we are closer
            # Earlier in the game => stronger push toward first reach.
            time_scale = 1.0 + (1.0 if tr <= 12 else 0.0) + (0.4 if tr <= 24 else 0.0)
            val += gap * (18.0 * time_scale)

            # Heavy penalty for giving opponent an edge on nearby/valuable resources.
            if opp_d <= my_d:
                # Penalize being not strictly closer; scale by proximity.
                prox = 9.0 - min(8, my_d)
                val -= (12.0 + prox) * (1.0 + (2.0 if opp_d <= 1 else 0.0))

            # Mild preference to reduce our own distance when contested.
            val += (1.5 if my_d <= 2 else 0.0) - (0.2 * my_d)

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]