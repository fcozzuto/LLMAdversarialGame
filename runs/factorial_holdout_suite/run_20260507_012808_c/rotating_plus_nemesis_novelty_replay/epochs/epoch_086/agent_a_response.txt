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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = manh(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    best_target = resources[0]
    best_score = -10**18
    my_now_best = manh(sx, sy, best_target[0], best_target[1])

    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        score = (opd - myd) * 10 - myd
        if score > best_score or (score == best_score and myd < my_now_best):
            best_score = score
            best_target = (rx, ry)
            my_now_best = myd

    rx, ry = best_target
    best_move = [0, 0]
    best_val = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = manh(nx, ny, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # Tie-break: keep advantage and approach target
        val = myd * 1000 - (opd - myd) * 10
        if val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move