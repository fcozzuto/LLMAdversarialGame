def choose_move(observation):
    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_terr = set(tuple(p) for p in observation.get("self_territory", []))
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def md(a, b):
        d = a - b
        return d if d >= 0 else -d

    def dist(px, py, qx, qy):
        return md(px, qx) + md(py, qy)

    # Deterministic target selection: prefer nearby unclaimed; otherwise contest opponent.
    if unclaimed:
        target = None
        best = 10**9
        for ux, uy in unclaimed:
            d = dist(x, y, ux, uy)
            # tie-breaker: closer to center
            t = d * 1000 + dist(ux, uy, cx, cy)
            if t < best:
                best = t
                target = (ux, uy)
    else:
        target = (ox, oy)

    best_move = [0, 0]
    best_val = -10**18
    best_tie = 10**18

    for i, (dx, dy) in enumerate(moves):
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in unclaimed:
            val += 900.0
        if (nx, ny) in opp_terr:
            val += 650.0  # flipping on entry
        if (nx, ny) in self_terr:
            val += 40.0

        # Frontier pressure: encourage moving toward unclaimed near the current territory.
        if self_terr:
            # Compute whether next cell is adjacent to unclaimed (cheap local check).
            adj_uncl = False
            for sx, sy in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 1, ny + 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx - 1, ny - 1)):
                if 0 <= sx < w and 0 <= sy < h and (sx, sy) in unclaimed:
                    adj_uncl = True
                    break
            if adj_uncl:
                val += 120.0

        # Contest: prefer stepping toward opponent position when no good unclaimed exists nearby.
        val += 6.0 * (dist(ox, oy, target[0], target[1]) - dist(ox, oy, nx, ny)) * 0.01

        # Primary tie metric: closer to chosen target; secondary: farther from opponent to reduce counterclaim.
        tie1 = dist(nx, ny, target[0], target[1])
        tie2 = -dist(nx, ny, ox, oy)
        tie = tie1 * 1000 + (tie2 if tie2 >= 0 else -tie2)

        if val > best_val or (val == best_val and (tie < best_tie or (tie == best_tie and i < 0))):
            best_val = val
            best_tie = tie
            best_move = [dx, dy]

    return best_move