def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    valid_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in valid_moves:
            v = d2(nx, ny, ox, oy)  # move away if no resources
            cand = (v, -dx, -dy)
            if best is None or cand > best:
                best = cand
                bestmove = (dx, dy)
        return [bestmove[0], bestmove[1]]

    # Opponent stays put for evaluation (fast greedy); pick move that maximizes "resource advantage"
    bestmove = (0, 0)
    bestv = -10**18
    for dx, dy, nx, ny in valid_moves:
        adv = -10**18
        for rx, ry in resources:
            sd = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent, otherwise still pick the best available.
            val = (od - sd) * 10 - sd
            # Small nudge toward actually collecting: closer to any resource slightly better.
            val += -0.1 * min(d2(nx, ny, px, py) for px, py in resources)
            if val > adv:
                adv = val
        # Extra tie-break: avoid approaching opponent unless it improves advantage.
        opp_pen = 0.05 * (d2(nx, ny, ox, oy))
        v = adv - opp_pen
        if v > bestv or (v == bestv and (dx, dy) < bestmove):
            bestv = v
            bestmove = (dx, dy)

    return [int(bestmove[0]), int(bestmove[1])]