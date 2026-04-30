def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp_pos(x, y):
        if x < 0 or x >= w or y < 0 or y >= h:
            return None
        if (x, y) in obstacles:
            return None
        return (x, y)

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy)

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        bestv = None
        for rx, ry in resources:
            selfd = dist((sx, sy), (rx, ry))
            oppd = dist((ox, oy), (rx, ry))
            v = (oppd - selfd) * 1000 - selfd  # prefer closer while farther from opponent
            if bestv is None or v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        p = clamp_pos(nx, ny)
        if p is None:
            continue
        nsx, nsy = p
        self_to_target = dist((nsx, nsy), (tx, ty))
        opp_to_target = dist((ox, oy), (tx, ty))
        # If target is adjacent, prioritize picking/arriving; otherwise, minimize self distance and keep away from opponent
        score = -self_to_target * 10 + (opp_to_target - self_to_target)
        # small tie-break: move that increases distance from opponent to reduce their interception chance
        score += dist((nx, ny), (ox, oy)) * 0.001
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]