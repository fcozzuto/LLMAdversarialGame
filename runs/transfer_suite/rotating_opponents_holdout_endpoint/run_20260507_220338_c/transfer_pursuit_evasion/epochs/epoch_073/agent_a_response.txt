def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("avoid" in role_s) or ("escape" in role_s)
    is_pursuer = ("pursuer" in role_s) or ("chaser" in role_s) or ("hunter" in role_s) or ("catch" in role_s) or ("pursuit" in role_s)
    pursue = is_pursuer or not is_evader

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy  # squared Euclidean for smoother tie-break

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        dist2 = cheb(nx, ny, ox, oy)
        # Prefer avoiding/approaching obstacles near the move
        adj_block = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                tx, ty = nx + adx, ny + ady
                if (tx, ty) in blocked:
                    adj_block += 1

        if pursue:
            score = -dist2 - 0.05 * adj_block
        else:
            score = dist2 - 0.05 * adj_block

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best