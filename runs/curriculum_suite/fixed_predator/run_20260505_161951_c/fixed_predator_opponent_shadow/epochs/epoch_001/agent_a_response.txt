def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    if not resources:
        # fallback: move away from opponent if possible
        best = [0, 0]
        best_d = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"] and (nx, ny) not in obstacles:
                    d = abs(nx - ox) + abs(ny - oy)
                    if d > best_d:
                        best_d = d
                        best = [dx, dy]
        return best

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose resource: prefer closer, but avoid those opponent can reach sooner
    best_res = None
    best_score = -10**18
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # higher score is better
        score = -ds
        if do < ds:
            score -= 3 * (ds - do) + 10
        # slight tie-break toward center
        score -= 0.01 * (abs(rx - 3.5) + abs(ry - 3.5))
        if score > best_score:
            best_score = score
            best_res = (rx, ry)

    tx, ty = best_res
    # Generate candidate moves and pick best by resulting distance to target,
    # plus a small penalty if moving closer to opponent.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"] and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))

    best = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in candidates:
        val = -dist((nx, ny), (tx, ty))
        # avoid giving chase opportunities
        val -= 0.2 * dist((nx, ny), (ox, oy))
        # prefer staying closer to target alignment (diagonal-friendly)
        val -= 0.01 * ((nx - tx) ** 2 + (ny - ty) ** 2)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]