def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    def king(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    if not resources:
        cx, cy = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                score = -king(nx, ny, cx, cy)
                if score > best_score:
                    best_score = score
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Immediate pick is always best
        immediate = 0
        if any(nx == rx and ny == ry for rx, ry in resources):
            immediate = 100000

        local_best = -10**18
        for rx, ry in resources:
            myd = king(nx, ny, rx, ry)
            opd = king(ox, oy, rx, ry)
            # Favor resources we can reach sooner than opponent (contested control)
            contested = opd - myd
            score = 5000 - myd * 20 + contested * 80
            if myd == 0:
                score += 200000
            local_best = score if score > local_best else local_best

        # Small tie-break: avoid stepping closer to opponent unless it helps capture
        opp_close = -king(nx, ny, ox, oy) * 2
        total = immediate + local_best + opp_close

        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]