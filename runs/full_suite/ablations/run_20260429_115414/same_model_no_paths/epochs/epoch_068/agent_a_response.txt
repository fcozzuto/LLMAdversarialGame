def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_block_pen(x, y):
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    p += 1
        return p

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Choose the resource that is currently closest to us from the candidate position.
        self_best_d = 10**9
        self_best = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < self_best_d:
                self_best_d = d
                self_best = (rx, ry)
        rx, ry = self_best
        opp_d = cheb(ox, oy, rx, ry)
        # Race heuristic: prefer resources where we're closer than opponent; also push closer even if both race.
        val = (opp_d - self_best_d) * 10 - self_best_d
        # Disincentivize getting near obstacles unless it helps.
        val -= adj_block_pen(nx, ny)
        # Tie-break deterministically by preferring moves that reduce our distance to that target.
        if val > best_val or (val == best_val and (self_best_d < cheb(sx, sy, rx, ry))):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]