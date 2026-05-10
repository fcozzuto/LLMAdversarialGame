def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Find a global target to guide stepping (deterministic).
    targets = list(unclaimed) if unclaimed else list(opp_terr)
    if targets:
        best_t = min(targets, key=lambda p: (md(p, (sx, sy)) + 0.25 * abs(p[0] - cx) + 0.25 * abs(p[1] - cy), md(p, (ox, oy))))
        tx, ty = best_t
    else:
        tx, ty = (cx, cy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        p = (nx, ny)
        # Local cell value: prioritize capturing unclaimed, then opponent territory.
        if p in opp_terr:
            cell = 55
        elif p in unclaimed:
            cell = 40
        elif p in self_terr:
            cell = 5
        else:
            cell = 10

        # Encourage approach to target and discourage moving away.
        dist = md(p, (int(tx), int(ty))) if isinstance(tx, int) else abs(nx - tx) + abs(ny - ty)
        approach = -dist

        # Slightly avoid giving immediate access to opponent by preferring cells farther from opponent.
        opp_dist = md(p, (ox, oy))
        opp_avoid = 0.02 * opp_dist

        # Keep mild center pressure.
        center = -(abs(nx - cx) + abs(ny - cy)) * 0.01

        score = cell + approach + opp_avoid + center

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]