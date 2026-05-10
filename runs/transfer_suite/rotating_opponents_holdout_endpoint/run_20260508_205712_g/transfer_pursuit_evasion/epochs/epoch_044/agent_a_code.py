def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_evader = ("evader" in role and "pursuer" not in role) or ("evader" in opp_role and "pursuer" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if free(x + dx, y + dy):
                c += 1
        return c

    best_move = (0, 0)
    if is_evader:
        # run from pursuer; avoid corners if they reduce mobility
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            mob = mobility(nx, ny)
            # deterministic tie-break: prefer moves that improve dist first, then mob, then lexicographic
            key = (dist, mob, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2), -dx, -dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
    else:
        # pursue evader greedily; if blocked, pick move with best distance decrease and mobility
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            mob = mobility(nx, ny)
            # deterministic tie-break: reduce dist first, then mobility, then lexicographic
            key = (-dist, mob, -abs(nx - ox) - abs(ny - oy), dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]