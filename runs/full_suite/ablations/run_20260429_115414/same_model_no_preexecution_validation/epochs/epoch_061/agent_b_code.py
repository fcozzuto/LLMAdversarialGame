def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def edge_block(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx or ddy:
                    if (x + ddx, y + ddy) in obstacles:
                        c += 1
        return c

    # Pick best resource by advantage + closeness, with a bias to avoid contested approaches.
    best_rx, best_ry = resources[0]
    best_val = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; if contested, prefer those where we are closer.
        val = (opd - myd) * 10 - myd
        # If resource sits near obstacles, it tends to be harder to contest: slight bonus.
        val += edge_block(rx, ry)
        # If opponent is already extremely close, reduce priority.
        if opd <= 1:
            val -= 8
        if val > best_val:
            best_val = val
            best_rx, best_ry = rx, ry

    # Choose move that maximizes next-step advantage and reduces distance to target.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, best_rx, best_ry)
        opd2 = cheb(ox, oy, best_rx, best_ry)
        # Main goal: increase our lead over opponent on the target.
        score = (opd2 - myd2) * 10 - myd2
        # Add a small anti-opponent term: move away when equally good.
        score -= cheb(nx, ny, ox, oy) * 0.1
        # Slightly prefer moves that tuck closer to obstacles (can block lines).
        score += edge_block(nx, ny) * 0.15
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move