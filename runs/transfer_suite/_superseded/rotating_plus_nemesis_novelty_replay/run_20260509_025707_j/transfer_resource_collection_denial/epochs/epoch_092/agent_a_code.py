def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Prefer moves that immediately create the biggest "catch advantage" on at least one resource.
    # If already winning for some resource, strongly pick the closest of them.
    best = None
    best_score = -10**18
    center_bias = (sx + sy) * 0.00001  # tiny deterministic tie-break

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Mild penalty for stepping adjacent to obstacles (avoid dead ends); deterministic and cheap.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj_obs += 1

        my_d_min_win = 10**9
        adv_best = -10**18
        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)

            # "catch advantage": how much closer we are than opponent after this move
            adv = (opp_d - my_d)

            # winning set: resources where we are not farther than opponent
            if my_d <= opp_d:
                if my_d < my_d_min_win:
                    my_d_min_win = my_d

            # emphasize larger advantage; also prefer earlier capture when time is short
            time_w = 1.0 + (0 if turns_remaining is None else min(12, max(0, turns_remaining))) / 20.0
            score_here = adv * time_w - 0.05 * my_d
            if score_here > adv_best:
                adv_best = score_here

        # If we can already be winning for something, prioritize the closest winning target.
        if my_d_min_win < 10**9:
            score = 10**6 - 5.0 * my_d_min_win + 50.0 * adv_best - 0.7 * adj_obs + center_bias
        else:
            # Otherwise, try to reduce the deficit the most and create best advantage.
            score = 1000.0 * adv_best - 0.5 * adj_obs + center_bias

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]