def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_value(px, py):
        if not resources:
            return (-10**9, 0)
        best = None
        for cx, cy in resources:
            self_d = cheb(px, py, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # Favor resources where we are closer than opponent; secondary: absolute closeness
            key = (opp_d - self_d, -self_d, -(abs(cx - ox) + abs(cy - oy)))
            if best is None or key > best[0]:
                best = (key, (cx, cy))
        return best[0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = (-10**18, -10**18)
    # If already on a resource cell, stay to secure
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        k = best_value(nx, ny)
        # Tie-break deterministically by prefer closer advancement then lower dx/dy lexicographically
        tie = (-abs(nx - sx) - abs(ny - sy), -abs(nx - ox) - abs(ny - oy))
        cand = (k[0], k[1])
        if cand > best_key:
            best_key = cand
            best_move = (dx, dy)
        elif cand == best_key:
            if tie > (-(abs(best_move[0]) + abs(best_move[1])), -abs(best_move[0] - ox) - abs(best_move[1] - oy)):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]