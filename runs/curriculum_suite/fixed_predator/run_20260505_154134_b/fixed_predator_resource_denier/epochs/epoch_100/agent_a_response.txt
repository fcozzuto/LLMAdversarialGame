def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_for(posx, posy):
        if not resources:
            return (w // 2, h // 2)
        best = None
        for tx, ty in resources:
            self_d = cheb(posx, posy, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # prefer resources we can reach sooner; if tie, prefer those further from opponent
            s = (self_d - opp_d, self_d, tx + ty)
            if best is None or s < best[0]:
                best = (s, (tx, ty))
        return best[1] if best else (w // 2, h // 2)

    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    # choose move by maximizing improvement towards best target while discouraging opponent blocking
    base_tx, base_ty = best_for(sx, sy)
    best_move = None
    best_score = None

    for dx, dy, nx, ny in legal:
        tx, ty = best_for(nx, ny)
        self_d0 = cheb(sx, sy, base_tx, base_ty)
        self_d1 = cheb(nx, ny, tx, ty)
        opp_d1 = cheb(ox, oy, tx, ty)
        # score: reduce our distance, increase opponent distance, small tie-break towards center/proximity
        score = (
            self_d0 - self_d1,
            opp_d1,
            -abs(nx - w // 2) - abs(ny - h // 2),
            -(nx + ny),
            dx,
            dy,
        )
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]