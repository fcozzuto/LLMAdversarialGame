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

    def mdist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if not resources:
        # Pressure if no resources visible
        best_dxdy = (10**9, 0, 0)
        for dx, dy, nx, ny in valid:
            d_to_opp = mdist(nx, ny, ox, oy)
            if d_to_opp < best_dxdy[0]:
                best_dxdy = (d_to_opp, dx, dy)
        return [best_dxdy[1], best_dxdy[2]]

    # Choose resource where we have the best "reach advantage"; slight tie-break to closeness.
    best = None  # (priority, myd, tx, ty)
    for tx, ty in resources:
        myd = mdist(sx, sy, tx, ty)
        opd = mdist(ox, oy, tx, ty)
        advantage = opd - myd  # higher is better (we are closer)
        # If we are already on it, take immediately
        if myd == 0:
            best = (10**6, 0, tx, ty)
            break
        pri = advantage * 100 - myd
        cand = (pri, myd, tx, ty)
        if best is None or cand[0] > best[0]:
            best = cand

    _, _, tx, ty = best

    # Move one step to reduce distance to target; if equal, prefer staying safer from opponent.
    best_move = None  # (score, dx, dy)
    for dx, dy, nx, ny in valid:
        myd = mdist(nx, ny, tx, ty)
        opd = mdist(nx, ny, ox, oy)
        # Strongly prefer progress; slight preference to be farther from opponent to avoid denial races.
        score = myd * 10 - opd
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]