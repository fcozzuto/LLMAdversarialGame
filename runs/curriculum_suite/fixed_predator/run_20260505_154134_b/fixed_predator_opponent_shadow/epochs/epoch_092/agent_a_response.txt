def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target where we are likely to be able to arrive before opponent.
    # Key: prefer (opp closer - us closer) smaller? We want us not too behind; maximize advantage.
    best = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        # Prefer higher (od - sd). Tie-breaker: nearer and more central-ish.
        key = (od - sd, -sd, -(cx + cy), -cx)
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)
    tx, ty = best

    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Choose move that improves: closer to target + farther from opponent (or reduces their edge)
    best_move = (0, 0)
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # Main: reduce our distance; secondary: reduce opponent's relative advantage
        val = (-sd2, -(od2 - sd2), -(abs(nx - ox) + abs(ny - oy)), -(nx + ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]