def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    neigh = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) not in obstacles:
                    neigh.append((dx, dy))

    if not neigh:
        return [0, 0]

    if resources:
        best = None
        for r in resources:
            rs = dist((sx, sy), r)
            ro = dist((ox, oy), r)
            score = (ro - rs, -rs)  # advantage, then closer
            if best is None or score > best[0]:
                best = (score, r)
        target = best[1]
    else:
        target = (ox, oy)  # fallback: head toward opponent

    tx, ty = target
    # Desired step toward target
    step_options = []
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        d = abs(nx - tx) + abs(ny - ty)
        # Also consider not moving closer for opponent when contesting
        if resources:
            opp_d = abs(nx - ox) + abs(ny - oy)
        else:
            opp_d = 0
        step_options.append((d, opp_d, dx, dy))

    step_options.sort()
    return [int(step_options[0][2]), int(step_options[0][3])]