def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w - 1 - sy if (sy < w) else w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        if (sx + dx, sy + dy) in obstacles:
            return [0, 0]
        return [dx, dy]

    # Deterministic tie-breaks:
    # 1) Maximize (opp_distance - my_distance) => prefer resources we reach earlier
    # 2) If close, prefer resources nearer to us
    # 3) If still tie, prefer lexicographically smaller (x,y)
    best = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        score = (opd - myd, -myd, -((rx * 8 + ry) % 9), -rx, -ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    _, (tx, ty) = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose the move that most reduces our distance to target; if blocked, fall back deterministically.
    best_move = (10**9, 10**9, 10**9, 0, 0)  # (d_to_target, blocked, oppd, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        blocked = 1 if (nx, ny) in obstacles else 0
        d_to = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        cand = (d_to, blocked, opd, dx, dy)
        if cand < best_move:
            best_move = cand
    dx, dy = int(best_move[3]), int(best_move[4])
    if (sx + dx, sy + dy) in obstacles:
        # Deterministic safe fallback: try staying, else a non-blocked step towards target axis.
        if (sx, sy) not in obstacles:
            return [0, 0]
        for dx2 in (-1, 0, 1):
            for dy2 in (-1, 0, 1):
                nx, ny = sx + dx2, sy + dy2
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [dx2, dy2]
        return [0, 0]
    return [dx, dy]