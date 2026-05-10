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

    if not resources:
        return [0, 0]

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        on_res_bonus = 6.0 if (nx, ny) in res_set else 0.0
        # Pick the best resource after this move by maximizing (op_dist - my_dist).
        best_diff = None
        best_tie = None
        best_my_d = None
        for rx, ry in res_list:
            my_d = dist(nx, ny, rx, ry)
            op_d = dist(ox, oy, rx, ry)
            diff = op_d - my_d
            key = (diff, -my_d, -rx, -ry)  # deterministic tie-breaking
            if best_diff is None or key > best_tie:
                best_tie = key
                best_diff = diff
                best_my_d = my_d

        # Value: prioritize being able to arrive no later than opponent; otherwise minimize their advantage.
        # Also lightly prefer closer overall.
        can_secure = 1.0 if best_diff >= 0 else 0.0
        val = on_res_bonus + (10.0 * can_secure) + (best_diff * 3.0) + (-0.15 * best_my_d)

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]