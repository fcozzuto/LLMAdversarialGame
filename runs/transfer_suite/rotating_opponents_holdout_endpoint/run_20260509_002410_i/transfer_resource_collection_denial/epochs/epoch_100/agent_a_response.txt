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
        nx = sx + dx; ny = sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = None; bestd = None
        for dx, dy in legal:
            nx = sx + dx; ny = sy + dy
            d = man(nx, ny, tx, ty)
            if best is None or d < bestd or (d == bestd and (dx, dy) < best):
                best = (dx, dy); bestd = d
        return [best[0], best[1]]

    best_r = None
    best_score = None
    for (rx, ry) in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        score = (od - sd) * 10 - sd + (ry * 0.01) + (rx * 0.001)
        key = (score, -sd, -od, rx, ry)
        if best_r is None or key > best_score:
            best_r = (rx, ry); best_score = key

    rx, ry = best_r

    best_move = None
    best_key = None
    for dx, dy in legal:
        nx = sx + dx; ny = sy + dy
        d = man(nx, ny, rx, ry)
        # Prefer immediate pickup and deny opponent by pushing toward contested resources
        next_od = man(ox, oy, rx, ry)
        key = (-1 if (nx == rx and ny == ry) else 0, (next_od - d), -d, dx, dy)
        # Deterministic: higher key preferred lexicographically
        if best_key is None or key > best_key:
            best_key = key; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]