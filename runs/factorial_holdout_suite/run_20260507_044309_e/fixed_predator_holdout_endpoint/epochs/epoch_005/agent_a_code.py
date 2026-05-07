def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # When no resources visible, drift toward opponent to deny and reduce their options
        best = None
        bestv = None
        for dx, dy in sorted(moves, key=lambda t: (t[0], t[1])):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            v = abs(nx - ox) + abs(ny - oy)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Deterministic evaluation: maximize advantage over opponent for reachable high-value resources
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in sorted(moves, key=lambda t: (t[0], t[1])):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer immediate collection, then best "who arrives first" advantage.
        val = 0
        for (rx, ry) in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # Reward collecting on this move (self_d==0) very strongly.
            if self_d == 0:
                val += 1000

            # If opponent is closer, heavily penalize; else reward.
            # Scale with distance to avoid oscillations.
            advantage = opp_d - self_d
            val += 20 * advantage - self_d

            # Slight preference for states that keep more resources reachable soon
            # (simple proxy: count resources where we are not worse than opponent).
        # Count proxy
        closer_count = 0
        for (rx, ry) in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            if self_d <= opp_d:
                closer_count += 1
        val += 2 * closer_count

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move