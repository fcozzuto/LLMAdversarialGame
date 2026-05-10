def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        ahead = 1 if sd < od else 0
        key = (ahead, -(sd), (od - sd), -rx - ry)
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary: get closer to chosen target.
        myd = cheb(nx, ny, tx, ty)

        # Secondary: if we can "win" another resource sooner than opponent, do so.
        win_bonus = 0
        threat = 0
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if md < od:
                win_bonus += 2 if md <= 1 else 1
            elif od < md:
                threat += 1 if od <= 1 else 0

        # Tertiary: keep moving generally toward center of target direction.
        toward = abs(tx - nx) + abs(ty - ny)

        # Score higher is better.
        score = (win_bonus * 100) - (myd * 10) - (threat * 25) - toward
        if best_score is None or score > best_score:
            best_score, best_step = score, (dx, dy)

    return [best_step[0], best_step[1]]