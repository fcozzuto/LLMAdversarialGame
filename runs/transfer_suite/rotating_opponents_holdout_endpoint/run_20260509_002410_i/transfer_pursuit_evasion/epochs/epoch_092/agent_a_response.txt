def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def near_obstacle(x, y):
        n = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    n += 1
        return n

    # Target selection is deterministic and changes strategy with position relative to opponent.
    if is_pursuer:
        primary = (ox, oy)
    else:
        # Evader aims to maximize distance; prefer opposite side from pursuer.
        tx = (0 if ox > (w - 1) / 2 else w - 1)
        ty = (0 if oy > (h - 1) / 2 else h - 1)
        # If line is blocked, bias toward farthest corner deterministically.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestc = None
        bestd = -1
        for cx, cy in corners:
            d = cheb(cx, cy, ox, oy)
            if d > bestd:
                bestd = d
                bestc = (cx, cy)
        tx, ty = bestc if bestd >= cheb(tx, ty, ox, oy) else (tx, ty)
        primary = (tx, ty)

    # Score moves: pursuer reduces distance to opponent; evader increases distance from opponent and to its escape target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_tgt = cheb(nx, ny, primary[0], primary[1])
        nobs = near_obstacle(nx, ny)
        if is_pursuer:
            score = (-d_opp, nobs, d_tgt)  # minimize distance, then minimize obstacle proximity
        else:
            score = (d_opp, -d_tgt, -nobs)  # maximize distance, then maximize progress away from target, then avoid obstacles
        if best_score is None or (score > best_score if not is_pursuer else score < best_score):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]