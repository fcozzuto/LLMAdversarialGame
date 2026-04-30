def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = md(nx, ny, ox, oy)  # run away when no resources
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Focus on contesting resources where the opponent is already relatively close.
    res_sorted = sorted(resources, key=lambda r: md(ox, oy, r[0], r[1]))
    focus = res_sorted[:6]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # One-step lookahead value: avoid moves where opponent gets the pick much earlier.
        val = 0
        for rx, ry in focus:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # If we would land on a resource, dominate.
            if ds == 0:
                val += 10**6
            # We gain when we reduce our distance faster than opponent.
            val += (do - ds) * (1.0 / (1 + do))
            # Penalty if opponent is clearly ahead on this resource (prevents "chasing" losing targets).
            if do + 1 <= ds:
                val -= 5.0 / (1 + ds)

        # Extra tie-break: prefer being closer to opponent's nearest focus resource if contested.
        nx0, ny0 = focus[0][0], focus[0][1]
        ds0 = md(nx, ny, nx0, ny0)
        val -= 0.05 * ds0

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]