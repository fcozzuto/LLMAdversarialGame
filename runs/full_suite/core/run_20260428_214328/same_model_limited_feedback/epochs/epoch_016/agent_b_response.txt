def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        # No resources visible: move toward opponent to contest
        tx, ty = ox, oy
    else:
        def dist(a, b, x, y):
            dx = a - x; dy = b - y
            if dx < 0: dx = -dx
            if dy < 0: dy = -dy
            return dx if dx > dy else dy  # Chebyshev for 8-direction
        best = None
        bestv = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; break ties by being closer to us
            v = (do - ds) * 10 - ds
            if best is None or v > bestv or (v == bestv and ds < bestv_ds):
                best = (rx, ry); bestv = v; bestv_ds = ds
        tx, ty = best if best is not None else resources[0]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try direct move first
    cand = (desired_dx, desired_dy)
    nx, ny = sx + cand[0], sy + cand[1]
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [cand[0], cand[1]]

    # Otherwise pick the safe move that most reduces distance to target
    bestm = (0, 0); bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d = max(abs(tx - nx), abs(ty - ny))
        if bestd is None or d < bestd or (d == bestd and (dx, dy) == (0, 0)):
            bestd = d; bestm = (dx, dy)
    return [bestm[0], bestm[1]]