def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = (w // 2, h // 2)
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, tx, ty)
            key = (-d, dx, dy)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1]

    center = (w // 2, h // 2)
    best_move = None
    best_key = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_res_key = None
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            beat = 1 if myd < opd else 0
            # Prefer beating resources; otherwise minimize our distance and secondarily keep away from being beaten.
            score = beat * 100000 - myd * 100 - opd
            # Small openness: prefer targets closer to center when tied.
            score += -man(rx, ry, center[0], center[1])
            # Tie-break deterministically by coordinates.
            key = (beat, score, -myd, -opd, -rx, -ry)
            if best_res_key is None or key > best_res_key:
                best_res_key = key
        key_move = (best_res_key, dx, dy)
        if best_key is None or key_move > best_key:
            best_key = key_move
            best_move = [dx, dy]

    return best_move