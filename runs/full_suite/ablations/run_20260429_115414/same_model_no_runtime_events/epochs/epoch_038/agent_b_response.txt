def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem)
    except:
        rem = len(resources)
    late = rem <= 4

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx0, dy0 in dirs:
        nx, ny = sx + dx0, sy + dy0
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose best resource relative to both agents from the candidate position.
        cand_best = -10**18
        cand_dist_to_win = 10**9
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent, and (when late) be aggressive.
            rel = opd - myd
            score = rel * 50 - myd * (8 if not late else 12)
            if rel >= 0:
                score += 200 - (0 if late else 0)
            # Small deterministic tie-breaker toward staying central-ish and toward lower coords.
            score += -(abs(rx - (w - 1) // 2) + abs(ry - (h - 1) // 2)) * 0.1
            if score > cand_best or (score == cand_best and (myd < cand_dist_to_win or (myd == cand_dist_to_win and (rx + ry) < (best_move[0] + best_move[1])))):
                cand_best = score
                cand_dist_to_win = myd

        # Additional safety: avoid getting too close to opponent unless it improves target score.
        risk = dist(nx, ny, ox, oy)
        cand_best -= (0 if late else (risk < 2) * 60)

        if cand_best > best_score:
            best_score = cand_best
            best_move = [dx0, dy0]

    return [int(best_move[0]), int(best_move[1])]