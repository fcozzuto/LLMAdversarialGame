def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = observation["resources"]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Target selection: prefer resources where we are relatively closer than the opponent.
    if resources:
        best_r = None
        for r in resources:
            rx, ry = r[0], r[1]
            d_self = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # Higher score means "more contested in our favor".
            score = (d_opp - d_self, -d_self, -rx, -ry)
            if best_r is None or score > best_r[0]:
                best_r = (score, (rx, ry))
        target = best_r[1]
    else:
        # No resources known: pressure by moving toward opponent.
        target = (ox, oy)

    # Move selection: greedy toward target, but avoid stepping adjacent to opponent if possible.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = dist((nx, ny), target)
        d_o = dist((nx, ny), (ox, oy))
        # If we can avoid getting too close, prefer that; otherwise just minimize target distance.
        penalty = 0 if d_o >= 2 else (2 - d_o) * 10
        key = (d_t + penalty, -d_o, nx, ny)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]