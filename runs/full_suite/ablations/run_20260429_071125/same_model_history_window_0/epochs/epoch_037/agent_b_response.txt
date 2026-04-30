def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    best_move = [0, 0]
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = candidates

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp = (ox, oy)
    selfp = (sx, sy)

    def choose_target():
        if not resources:
            return None
        best = None
        best_score = None
        for r in resources:
            rd = dist(selfp, r)
            od = dist(opp, r)
            # Prefer resources we can reach sooner; otherwise prefer central-ish tie-break.
            sc = (od - rd) * 100 - rd + (3 - abs(r[0] - (w - 1) / 2)) * 0.01 + (3 - abs(r[1] - (h - 1) / 2)) * 0.01
            if best is None or sc > best_score or (sc == best_score and (r[0], r[1]) < (best[0], best[1])):
                best = r
                best_score = sc
        return best

    target = choose_target()

    def eval_pos(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        score = 0.0
        if target is not None:
            score += -dist((nx, ny), target)
            # If stepping onto a resource, add big reward
            if [nx, ny] in resources or (nx, ny) in set(tuple(p) for p in resources):
                score += 1000
        # Avoid moving away from resources when target is None
        else:
            if resources:
                nearest = min(resources, key=lambda r: dist((nx, ny), r))
                score += -dist((nx, ny), nearest)
                if [nx, ny] == nearest:
                    score += 1000
        # Discourage allowing opponent to get closer to the target
        if target is not None:
            score -= 0.2 * (dist(opp, target) - dist((ox, oy), target))
        # Penalty for proximity to opponent to reduce collision/hand-off
        score -= 0.15 / (1 + dist((nx, ny), opp))
        # Slight preference for staying within bounds already handled
        return score

    res_set = set(tuple(p) for p in resources)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = eval_pos(nx, ny)
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]