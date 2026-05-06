def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty)
            opp_tie = cheb(nx, ny, ox, oy)
            cand = (v, -opp_tie, -dx, -dy)
            if best is None or cand > best:
                best = cand
        return [best[2] * -1 if best else 0, best[3] * -1 if best else 0]

    best_cand = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        best_margin = -10**9
        best_sd = 10**9
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - self_d
            if margin > best_margin or (margin == best_margin and self_d < best_sd):
                best_margin = margin
                best_sd = self_d
        # Prefer moves that keep the opponent relatively far while improving margin
        opp_prox = cheb(nx, ny, ox, oy)
        cand = (best_margin, -best_sd, -opp_prox, -dx, -dy)
        if best_cand is None or cand > best_cand:
            best_cand = cand
    return [-best_cand[3] if best_cand else 0, -best_cand[4] if best_cand else 0]