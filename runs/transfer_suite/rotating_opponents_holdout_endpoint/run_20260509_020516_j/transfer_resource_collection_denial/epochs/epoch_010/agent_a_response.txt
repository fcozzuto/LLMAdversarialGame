def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    candidates = []
    if resources:
        for rx, ry in resources:
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                myd = abs(sx - rx) + abs(sy - ry)
                od = abs(ox - rx) + abs(oy - ry)
                adv = od - myd  # positive if we are closer
                center_bias = -((rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2) / 10.0
                candidates.append((adv, -myd, center_bias, rx, ry))
        candidates.sort(reverse=True)
    else:
        candidates = []
    if not candidates:
        return [0, 0]
    top = candidates[:6]
    best_move, best_score = [0, 0], None

    # Evaluate moves by how much advantage we create on top resources.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0.0
        for i, (adv, neg_my_d, cb, rx, ry) in enumerate(top):
            myd2 = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            adv2 = od - myd2
            # Strong preference to secure a resource (adv2>0), otherwise reduce deficit.
            score += (adv2 * 5.0) + (-myd2) * (0.35 / (1 + i)) + cb * (0.2 / (1 + i))
            if adv2 > 0 and myd2 == 0:
                score += 50.0
        # Slightly prefer moves that progress toward the best-ranked target to avoid dithering.
        score += -abs((nx - top[0][3])) - abs((ny - top[0][4]))
        if best_score is None or score > best_score:
            best_score, best_move = score, [dx, dy]

    return best_move