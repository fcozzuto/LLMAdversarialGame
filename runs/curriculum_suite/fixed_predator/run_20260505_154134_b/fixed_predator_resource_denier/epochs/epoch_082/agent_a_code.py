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

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = w // 2, h // 2

    if not resources:
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            val = (cheb(nx, ny, ox, oy) - cheb(nx, ny, cx, cy), -cheb(nx, ny, sx, sy))
            if best is None or val > best[0]:
                best = (val, (dx, dy))
        return list(best[1]) if best else [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Deny: focus on resources the opponent is likely to take (small opp distance),
        # but prefer moves where we become closer than the opponent.
        best_cell = None
        min_self_to_any = None
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if min_self_to_any is None or self_d < min_self_to_any:
                min_self_to_any = self_d
            cell = (opp_d - self_d, -self_d, -opp_d)  # primary: be closer than opponent
            if best_cell is None or cell > best_cell:
                best_cell = cell

        # Small progress bias to avoid oscillations between equally-denying cells.
        score = (best_cell[0], best_cell[1], -(min_self_to_any if min_self_to_any is not None else 0))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]