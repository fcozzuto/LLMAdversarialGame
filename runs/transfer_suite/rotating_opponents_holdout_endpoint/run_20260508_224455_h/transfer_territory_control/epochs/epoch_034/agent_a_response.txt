def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for c in (observation.get("obstacles", []) or []):
        try:
            x, y = c
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))
    unclaimed_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer: immediate flip opp territory > claim unclaimed > stay/expand,
    # while drifting toward center and keeping a bit of separation from opponent.
    best = [0, 0]
    best_val = -10**9
    opp_pos = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in opp_set:
            val += 6.0
        elif (nx, ny) in unclaimed_set:
            val += 3.5
        elif (nx, ny) in self_set:
            val += 1.0

        # Center attraction
        val += 1.2 * (-((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)))

        # Slightly avoid being too close to opponent unless we can flip now
        if (nx, ny) not in opp_set:
            val += -0.35 * md((nx, ny), (ox, oy))

        # Tie-break deterministically: smallest (abs(dx)+abs(dy)), then lexicographic
        move_cost = abs(dx) + abs(dy)
        if val > best_val or (abs(val - best_val) < 1e-9 and (move_cost, dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1])):
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]