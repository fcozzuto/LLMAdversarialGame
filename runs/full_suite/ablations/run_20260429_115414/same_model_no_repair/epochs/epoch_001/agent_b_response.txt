def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target = None
    if resources:
        best = None
        for r in resources:
            d_self = dist((x, y), r)
            d_opp = dist((ox, oy), r)
            # Prefer reachable targets where we are not much worse than opponent.
            key = (d_self - 0.85 * d_opp, d_self, r[0], r[1])
            if best is None or key < best:
                best = key
                target = r

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic preference order toward target: reduce distance, then closer to center.
    if target is None:
        tx, ty = cx, cy
    else:
        tx, ty = target[0], target[1]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # If we're heading to a resource, reward being on it strongly.
        if target is not None and (nx, ny) == target:
            score = -10_000_000
        else:
            d_to_target = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            d_to_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            d_to_center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            # Balance: get closer to target while not letting opponent freely approach.
            score = (d_to_target, -0.15 * d_to_opp, d_to_center, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]