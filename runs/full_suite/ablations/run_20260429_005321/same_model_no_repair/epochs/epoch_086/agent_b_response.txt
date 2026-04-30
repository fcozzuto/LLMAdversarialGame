def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_moves(x, y):
        out = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                out.append((dx, dy, nx, ny))
        return out or [(0, 0, x, y)]

    if not resources:
        tx, ty = (0 if sx > (w - 1) // 2 else w - 1), (0 if sy > (h - 1) // 2 else h - 1)
        legal = legal_moves(sx, sy)
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) == (0, 0)):
                best = (d, dx, dy)
        return [best[1], best[2]]

    R = {(r[0], r[1]) for r in resources}
    legal = legal_moves(sx, sy)
    best_score = None
    best_move = [0, 0]
    for dx, dy, nx, ny in legal:
        minr = None
        for rx, ry in R:
            d = cheb(nx, ny, rx, ry)
            if minr is None or d < minr:
                minr = d
        if minr is None:
            minr = 0
        landing_bonus = -5 if (nx, ny) in R else 0
        dop = cheb(nx, ny, ox, oy)
        # Prefer getting closer to resources; keep distance from opponent to reduce competition.
        score = (minr * 10) + (dop) + landing_bonus
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: prefer staying still, then lexicographically smaller move.
            if (dx, dy) == (0, 0) and (best_move[0], best_move[1]) != (0, 0):
                best_move = [dx, dy]
            elif (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]
    return best_move