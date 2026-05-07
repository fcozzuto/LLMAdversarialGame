def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy
    resources = observation.get("resources") or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None; best_d = 10**9; best_i = 10**9
        for i, (dx, dy, nx, ny) in enumerate(valid):
            d = dist(nx, ny, tx, ty)
            if d < best_d or (d == best_d and i < best_i):
                best = (dx, dy); best_d = d; best_i = i
        return [best[0], best[1]]

    # Deterministic competitive heuristic: prefer resources we can reach strictly sooner,
    # otherwise still go to close resources but penalize "contested" ones.
    opp_dists = [dist(ox, oy, r[0], r[1]) for r in resources]
    best_move = (0, 0); best_val = -10**18; best_i = 10**18
    for i, (dx, dy, nx, ny) in enumerate(valid):
        val = 0
        for (rx, ry), od in zip(resources, opp_dists):
            my = dist(nx, ny, rx, ry)
            # Strong preference for "wins" in approach time; mild tie-break against contests.
            if my < od:
                val += 30 / (my + 1) + (od - my) * 2
            elif my == od:
                val -= 8 / (my + 1)
            else:
                val -= 3 / (my + 1) + 0.5 / (od + 1)
        # Small tie-break: avoid stepping away from all resources.
        nearest_my = min(dist(nx, ny, r[0], r[1]) for r in resources)
        val -= nearest_my * 0.05
        if val > best_val or (val == best_val and i < best_i):
            best_val = val; best_move = (dx, dy); best_i = i
    return [best_move[0], best_move[1]]