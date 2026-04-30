def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def obstacle_near(x, y):
        if not obstacles:
            return 0
        best = 999
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best_res = None
    best_score = -10**18
    for x, y in resources:
        d_us = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)
        # Prefer resources we can reach earlier than opponent.
        # Tie-break by safer paths (far from obstacles).
        diff = d_op - d_us  # positive => advantage
        near = obstacle_near(x, y)
        safety = 0 if near >= 3 else (3 - near) * 3
        cur_pen = cheb(sx, sy, x, y)  # slight preference for closer
        score = diff * 200 - safety - cur_pen
        if score > best_score:
            best_score = score
            best_res = (x, y)

    tx, ty = best_res
    # Pick move that best approaches target, while keeping distance from opponent.
    best_move = None
    best_mscore = -10**18
    # Deterministic tie-break order: sorted by (dx,dy)
    legal_sorted = sorted(legal)
    for dx, dy in legal_sorted:
        nx, ny = sx + dx, sy + dy
        d_to = cheb(nx, ny, tx, ty)
        d_from_op = cheb(nx, ny, ox, oy)
        # small incentive to not get too close to opponent
        mscore = (-d_to * 50) + (d_from_op * 2) - (obstacle_near(nx, ny) * 0.5)
        # If already at target (resource would be collected), stay is fine
        if nx == tx and ny == ty:
            mscore += 10**6
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]