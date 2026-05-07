def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        return [0, 0]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]

    def bfs_dist(stx, sty, gx, gy):
        if (stx, sty) == (gx, gy):
            return 0
        q = [(stx, sty)]
        d = {(stx, sty): 0}
        while q:
            x, y = q.pop(0)
            nd = d[(x, y)] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) not in d:
                    if (nx, ny) == (gx, gy):
                        return nd
                    d[(nx, ny)] = nd
                    q.append((nx, ny))
        return 10**9

    scores = observation.get("scores", {})
    my_score = scores.get(observation["self_name"], 0.0) if isinstance(scores, dict) else 0.0
    opp_score = scores.get(observation["opponent_name"], 0.0) if isinstance(scores, dict) else 0.0
    behind = my_score < opp_score

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            my_t = bfs_dist(nx, ny, rx, ry)
            op_t = bfs_dist(ox, oy, rx, ry)
            if my_t < my_best:
                my_best, opp_best = my_t, op_t

        # Move valuation: prioritize captures (my_t <= opp_t), and if behind, be aggressive.
        # If ahead, slightly prefer denials (making opp's lead smaller).
        for rx, ry in resources:
            my_t = bfs_dist(nx, ny, rx, ry)
            op_t = bfs_dist(ox, oy, rx, ry)
            win_margin = op_t - my_t  # positive means I arrive first
            val = (0,)
            if behind:
                # aggressive: strongly prefer winning a resource soonest
                val = (1 if my_t <= op_t else 0, win_margin, -my_t, -abs(rx - nx) - abs(ry - ny), rx, ry)
                if best_val is None or val > best_val:
                    best_val, best_move = val, (dx, dy)
            else:
                # defensive/denial: allow some slower captures, but reduce opponent advantage
                val = (1 if my_t <= op_t else 0, -abs(win_margin), -my_t, -op_t, rx, ry)
                if best_val is None or val > best_val:
                    best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]