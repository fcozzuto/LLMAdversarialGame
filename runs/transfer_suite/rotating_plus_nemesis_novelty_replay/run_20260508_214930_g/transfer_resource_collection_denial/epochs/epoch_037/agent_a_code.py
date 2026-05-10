def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    move_best = None
    move_best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Score based on best resource from the next position
        best_for_move = None
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            lead = oppd - myd  # positive => we are earlier or equal
            center = abs(rx - cx) + abs(ry - cy)
            # Encourage winning the collection race; discourage targets we can't beat
            sc = lead * 80 - myd * 1.5 - center * 0.15
            if best_for_move is None or sc > best_for_move:
                best_for_move = sc
        # Tie-break deterministically toward progressing (lower distance-to-best)
        if move_best_sc is None or best_for_move > move_best_sc:
            move_best_sc = best_for_move
            move_best = [dx, dy]
        elif best_for_move == move_best_sc:
            # Prefer moves that reduce chebyshev distance to opponent-favored nearby resources
            # (deterministic secondary key)
            key_curr = cheb(nx, ny, ox, oy)
            key_best = cheb(sx + move_best[0], sy + move_best[1], ox, oy) if move_best else 10**9
            if key_curr < key_best:
                move_best = [dx, dy]

    return move_best if move_best is not None else [0, 0]