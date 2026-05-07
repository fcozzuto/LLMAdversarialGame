def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    # If multiple moves tie, choose deterministically by move order then coordinates.
    best_score = -10**18
    best_move = (0, 0)

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue

        my_best = None
        score = -10**18

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my_t = dist(nx, ny, rx, ry)
            op_t = dist(ox, oy, rx, ry)

            # New policy: strongly prefer resources where we are strictly earlier.
            # If not earlier, prefer those that reduce the opponent advantage and/or are closer to us.
            if my_t < op_t:
                val = 10**9 - my_t * 10**5 + (op_t - my_t) * 10**4 + (rx + 2 * ry) * 0.001
            else:
                # Contested or worse: minimize (my_t - op_t) penalty; still move toward near resources.
                val = - (my_t - op_t) * 10**6 - my_t * 10**3 + (op_t) * 10**2 + (rx + 2 * ry) * 0.001

            if my_best is None or val > score:
                score = val
                my_best = (rx, ry)

        if score > best_score:
            best_score = score
            best_move = (mdx, mdy)
        elif score == best_score:
            if (mdx, mdy) < best_move:
                best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]