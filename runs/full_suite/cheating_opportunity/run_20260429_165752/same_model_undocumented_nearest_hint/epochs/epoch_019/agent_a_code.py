def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        tx = (W - 1 + sx) // 2
        ty = (H - 1 + sy) // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    rem = int(observation.get("remaining_resource_count") or len(resources))
    # Target selection: maximize "how much earlier we can get" vs opponent, but also counter when we are behind.
    target = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        lead = d_opp - d_self  # positive means we are earlier
        # If we're behind a lot, prefer resources far from opponent (deny).
        deny = d_opp - d_self
        score = (lead * 100) + (deny * (30 if rem <= 6 else 15))
        # Small tie-break: closer to us to reduce dithering.
        score -= d_self
        if d_opp == d_self:
            score += 5  # slight preference for contested ones we can reach soon
        if score > best_score:
            best_score = score
            target = (rx, ry)

    tx, ty = target
    # Move selection: go toward target; tie-break by improving relative position vs opponent.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        # Relative improvement key: maximize opponent distance minus our distance after move (using current opponent pos).
        rel = cheb(ox, oy, tx, ty) - d_to
        # Also discourage stepping away when already close.
        step_away_pen = 0
        if cheb(sx, sy, tx, ty) < d_to:
            step_away_pen = 2
        key = (-d_to, -rel, step_away_pen, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]