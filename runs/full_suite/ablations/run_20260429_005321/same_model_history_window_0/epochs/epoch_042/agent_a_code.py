def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set(tuple(p) for p in (observation["obstacles"] or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # No resources: move to maximize distance from opponent while staying safe
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = dist((nx, ny), (ox, oy))
                val = (d, -abs(dx) - abs(dy), -(dx * 2 + dy))
                if best is None or val > best[0]:
                    best = (val, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Pick a resource we are relatively closer to than the opponent.
    best_res = None
    best_val = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer resources where we are closer; tie-break by shorter self distance.
        val = (od - sd, -sd, -((rx + ry) + observation["turn_index"]) % 7)
        if best_val is None or val > best_val:
            best_val = val
            best_res = (rx, ry)

    rx, ry = best_res

    # Evaluate moves toward chosen resource, while not letting opponent cut us off too easily.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            self_d = dist((nx, ny), (rx, ry))
            opp_d = dist((nx, ny), (ox, oy))
            # Also discourage stepping into squares where opponent is closer to the same target.
            opp_self_d = dist((ox, oy), (rx, ry))
            val = (
                -self_d,
                opp_d,
                (opp_self_d - self_d),
                -abs(dx) - abs(dy),
                -((nx + ny) + (observation["turn_index"] % 3)) % 5,
            )
            moves.append((val, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0], reverse=True)
    return [moves[0][1], moves[0][2]]