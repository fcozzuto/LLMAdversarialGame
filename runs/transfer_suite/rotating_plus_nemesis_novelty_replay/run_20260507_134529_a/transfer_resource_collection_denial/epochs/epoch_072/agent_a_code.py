def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = manh(nx, ny, ox, oy)
            if v > best[0] or (v == best[0] and (nx, ny) < (best[1], best[2])):
                best = (v, nx, ny)
        return [best[1] - sx, best[2] - sy]

    # Prefer moves that win the race: maximize (opp_dist - self_dist) to the best resource.
    best_score = (-10**18, 10**9, 0, 0)
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        # Evaluate our best "contested" resource from (nx, ny)
        local_best = (-10**18, 10**9)
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Primary: how much closer we are than opponent (positive is good).
            # Secondary: smaller our distance.
            cand = (od - sd, -sd)
            if cand[0] > local_best[0] or (cand[0] == local_best[0] and sd < local_best[1]):
                local_best = (cand[0], sd)

        score1 = local_best[0]
        score2 = local_best[1]
        if (score1 > best_score[0]) or (score1 == best_score[0] and (score2 < best_score[1] or (score2 == best_score[1] and (nx, ny) < (best_score[2], best_score[3])))):
            best_score = (score1, score2, nx, ny)
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]