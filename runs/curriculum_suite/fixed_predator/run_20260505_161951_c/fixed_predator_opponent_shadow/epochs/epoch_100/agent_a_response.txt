def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (md(nx, ny, tx, ty), md(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Precompute for tie-breaking
    best_overall = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        self_ds = [md(nx, ny, rx, ry) for rx, ry in resources]
        opp_ds = [md(ox, oy, rx, ry) for rx, ry in resources]
        self_min = min(self_ds)
        opp_min = min(opp_ds)
        delta = opp_min - self_min  # positive means we are closer to the nearest resource than opponent
        opp_dist_new = md(nx, ny, ox, oy)

        # Choose which side is "winning" this step: deny opponent while staying resource-relevant
        # Higher score is better; use integer scaling for determinism.
        score = 50 * delta + 2 * opp_dist_new - self_min

        # Secondary heuristic: if scores tie, move toward the best resource we can realistically contest
        self_min_idx = self_ds.index(self_min)
        tx, ty = resources[self_min_idx]
        dist_to_that = md(nx, ny, tx, ty)

        key = (-score, dist_to_that, self_min, -opp_dist_new, dx, dy)
        if best_overall is None or key < best_overall[0]:
            best_overall = (key, (dx, dy))

    return [best_overall[1][0], best_overall[1][1]]