def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid_res.append((x, y))
    if not valid_res:
        return [0, 0]

    # Choose best target deterministically: maximize chance to reach first, then prioritize closer.
    best = None
    for rx, ry in valid_res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If equal reach times, slightly prefer nearer.
        key = (do - ds, -ds, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # One-step lookahead: pick move maximizing (reach-first pressure on best target + optional resource)
    # while avoiding obstacles/out-of-bounds.
    best_move = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        # Target pressure
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        score = (op_d - my_d) * 100 - my_d

        # Small opportunistic bonus: if move also gets us closer to any other resource.
        # Evaluate only top-3 by closeness from current position for brevity.
        cands = sorted(valid_res, key=lambda p: cheb(sx, sy, p[0], p[1]))[:3]
        score += max(0, 5 - min(cheb(nx, ny, px, py) for px, py in cands))

        # Deterministic tie-break: prefer moves with smaller dx, then smaller dy, then earlier in list.
        tb = (-abs(dx), -abs(dy), -dx, -dy)
        total = (score, tb)
        if best_move[0] is None or total > best_move[1]:
            best_move = ((dx, dy), total)
    return [int(best_move[0][0]), int(best_move[0][1])]