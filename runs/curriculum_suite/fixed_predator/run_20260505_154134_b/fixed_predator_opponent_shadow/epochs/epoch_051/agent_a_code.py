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

    if not resources:
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            k = (-cheb(nx, ny, ox, oy), cheb(nx, ny, sx, sy), -nx, -ny)
            if best_key is None or k > best_key:
                best_key, best = k, (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Interceptor focus: contest the resource currently closest to the opponent.
    focus = None
    best_opp = None
    for cx, cy in resources:
        d = cheb(ox, oy, cx, cy)
        if best_opp is None or d < best_opp or (d == best_opp and (cx < focus[0] or (cx == focus[0] and cy < focus[1]))):
            best_opp = d
            focus = (cx, cy)
    fx, fy = focus

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_res = cheb(nx, ny, fx, fy)
        opp_res = cheb(ox, oy, fx, fy)  # compare vs opponent's current ability
        # Intercept: (1) make us closer to focus than opponent (opp_res - self_res)
        # (2) also move toward opponent to block/steal turn tempo
        self_opp = cheb(nx, ny, ox, oy)
        k = (opp_res - self_res, -self_res, -self_opp, -nx, -ny)
        if best_key is None or k > best_key:
            best_key = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]