def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = [(p[0], p[1]) for p in observation.get("resources", [])]
    res_set = set(resources)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles or sx + dx < 0 or sx + dx >= w or sy + dy < 0 or sy + dy >= h:
            cands = []
            for ddx, ddy in deltas:
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    cands.append((dist((nx, ny), (tx, ty)), dist((nx, ny), (ox, oy)), ddx, ddy))
            if not cands:
                return [0, 0]
            cands.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
            return [cands[0][2], cands[0][3]]
        return [dx, dy]

    if resources:
        best = None
        for rx, ry in resources:
            d = dist((sx, sy), (rx, ry))
            # deterministic tie-break: prioritize smaller dx/dy direction then position order
            key = (d, abs(rx - sx) == 0 and abs(ry - sy) > 0, abs(ry - sy) == 0, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        _, rx, ry = best
        return step_toward(rx, ry)

    # No resources left: drift toward opponent to maximize tie-break disruption
    best_move = [0, 0]
    best_score = None
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        score = (-(abs(nx - ox) + abs(ny - oy)), ddx, ddy)  # move closer to opponent
        if best_score is None or score < best_score:
            best_score = score
            best_move = [ddx, ddy]
    return best_move