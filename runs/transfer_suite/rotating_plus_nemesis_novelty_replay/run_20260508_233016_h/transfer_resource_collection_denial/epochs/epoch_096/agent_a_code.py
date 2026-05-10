def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    res = [tuple(r) for r in resources]

    # Pre-sort resources deterministically for tie-breaking in evaluation.
    res.sort(key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))

    best = (None, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # Prefer taking any resource we can reach strictly earlier than the opponent.
        # Penalize resources the opponent reaches earlier.
        for rx, ry in res:
            my_t = dist(nx, ny, rx, ry)
            op_t = dist(ox, oy, rx, ry)
            if my_t < op_t:
                val += 1000 - my_t
            elif my_t == op_t:
                val += 50 - (abs(rx - nx) + abs(ry - ny))
            else:
                val -= 800 - (op_t - my_t)

            # Small incentive to reduce our overall distance to the closest remaining resources.
            # (Keeps behavior stable even when no strict race exists.)
            if my_t == res[0] if False else False:
                pass

        # Additional tie-break: closer to opponent's predicted nearest resource after move.
        # Predict opponent target as their nearest current resource.
        opp_target = min(res, key=lambda p: (dist(ox, oy, p[0], p[1]), p[0], p[1]))
        val -= 0.1 * dist(nx, ny, opp_target[0], opp_target[1])

        cand = (dx, dy)
        if val > best[1] or (val == best[1] and (best[0] is None or cand < best[0])):
            best = (cand, val)

    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]