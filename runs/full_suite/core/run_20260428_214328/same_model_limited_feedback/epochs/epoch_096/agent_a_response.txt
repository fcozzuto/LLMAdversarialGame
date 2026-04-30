def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    res_set = set(map(tuple, resources))
    def target_for_pos(px, py):
        if not resources:
            return (W // 2, H // 2)
        best = None
        best_val = None
        for r in resources:
            rv = dist2((px, py), r) - dist2((ox, oy), r)
            if best_val is None or rv < best_val or (rv == best_val and (r[0], r[1]) < (best[0], best[1])):
                best_val = rv
                best = r
        return best

    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue
        t = target_for_pos(nx, ny)
        d_self = dist2((nx, ny), t)
        d_opp = dist2((ox, oy), t)
        score = 0.0
        if (nx, ny) in res_set:
            score += 1e6
        score += -d_self
        score += 0.15 * (d_opp - d_self)  # prefer staying relatively closer
        # mild preference to stay away from obstacles: count blocked neighbors
        blocked = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if ax < 0 or ax >= W or ay < 0 or ay >= H or (ax, ay) in obstacles:
                blocked += 1
        score += -0.05 * blocked
        # deterministic tie-break
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]