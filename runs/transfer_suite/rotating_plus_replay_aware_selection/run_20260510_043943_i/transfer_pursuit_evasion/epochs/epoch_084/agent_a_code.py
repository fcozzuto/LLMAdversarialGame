def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evasion" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]

    def obstacle_risk(nx, ny):
        r = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d == 0: return 10**6
            if d == 1: r += 4
            elif d == 2: r += 1
        return r

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        dist = cheb(nx, ny, ox, oy)
        risk = obstacle_risk(nx, ny)

        # Small deterministic tie-breaker: prefer moves with earlier delta index naturally.
        # Score: evader wants larger dist, pursuer wants smaller dist; both avoid obstacles.
        score = (dist * (1 if is_evader else -1)) - risk
        if best_score is None or (score > best_score if is_evader else score < best_score):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]