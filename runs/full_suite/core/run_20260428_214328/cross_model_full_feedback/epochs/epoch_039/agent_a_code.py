def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def best_target(px, py):
        if not res:
            return None
        bestd = None
        best = None
        for rx, ry in res:
            d = cheb(px, py, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx < best[0] or (rx == best[0] and ry < best[1]))):
                bestd = d
                best = (rx, ry)
        return best

    self_t = best_target(sx, sy)
    opp_t = best_target(ox, oy)

    # If our target disappears, pick something deterministic from remaining resources
    if self_t is None and res:
        self_t = min(res)

    best_score = None
    best_move = (0, 0)

    for dx, dy, nx, ny in legal:
        # Avoid stepping onto opponent if possible (engine may keep you in place anyway)
        if (nx, ny) == (ox, oy):
            continue
        sd = cheb(nx, ny, self_t[0], self_t[1]) if self_t is not None else 0
        od = cheb(nx, ny, opp_t[0], opp_t[1]) if opp_t is not None else 0
        # Also estimate opponent progress: compare their distance to our candidate best target next turn
        opp_sd = cheb(ox, oy, self_t[0], self_t[1]) if self_t is not None else 0
        # Score: primarily minimize self distance; then maximize creating delay for opponent by increasing their distance to our target
        # Delay heuristic uses whether we move toward/away from the opponent's likely approach.
        delay = (cheb(ox, oy, self_t[0], self_t[1]) if self_t is not None else 0)
        # Prefer moving to reduce our distance and to move away from opponent, small tie-break
        score = (-10 * sd) + (2 * od) + (1.0 * (delay - cheb(ox, oy, self_t[0], self_t[1]) if self_t is not None else 0))
        # Deterministic tie-break: closer manhattan to center, then lexicographic dx,dy
        center = (w // 2, h // 2)
        center_pen = cheb(nx, ny, center[0], center[1])
        score2 = (score, -center_pen, -dx, -dy)

        if best_score is None or score2 > best_score:
            best_score = score2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]