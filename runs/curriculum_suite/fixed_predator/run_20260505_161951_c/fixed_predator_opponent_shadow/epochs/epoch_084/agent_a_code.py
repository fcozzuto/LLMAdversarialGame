def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (dist(nx, ny, tx, ty), dist(nx, ny, ox, oy), abs(nx - tx) + abs(ny - ty))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    best_key = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy

        # Prefer moves that make us closer to some resource than opponent (interception),
        # while also reducing our own distance to the best such resource.
        best_intercept = None
        best_resource_dist = None
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            rel = ds - do  # negative => we are closer than opponent
            # break ties toward smaller absolute distances
            cand = (rel, ds, do)
            if best_intercept is None or cand < best_intercept:
                best_intercept = cand
                best_resource_dist = ds

        # If no strong interception, still prefer decreasing nearest-resource distance,
        # but discourage getting too close to the opponent (avoid shared competition).
        opp_prox = dist(nx, ny, ox, oy)
        # reward getting closer to resources; penalize being near opponent
        key = (best_intercept[0], best_intercept[1], -opp_prox, best_resource_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]