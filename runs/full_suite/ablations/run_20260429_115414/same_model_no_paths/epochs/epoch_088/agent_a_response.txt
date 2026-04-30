def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Deterministic candidate target:
    # If resources exist, choose one where our reach is earlier than opponent (strong contest),
    # else choose the one minimizing opponent advantage against us (least bad).
    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            advantage = opd - myd  # positive = we arrive earlier
            # Prefer larger advantage; tie-break by closer myd; then coords.
            key = (-advantage, myd, rx, ry) if advantage < 0 else (-advantage, myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No visible resources: shift toward center but also toward the opponent's side less (avoid getting trapped).
        tx, ty = w // 2, h // 2
        if (sx <= w // 2) == (ox <= w // 2):
            tx = 1 if sx < w // 2 else w - 2
        if (sy <= h // 2) == (oy <= h // 2):
            ty = 1 if sy < h // 2 else h - 2

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd_next = cheb(nx, ny, tx, ty)
        opd_next = cheb(ox, oy, tx, ty)
        # Prefer reaching target quickly, while ensuring we are not getting dominated.
        score = -myd_next * 10 - (opd_next - myd_next < 0) * 50  # if we're slower than opp, penalize heavily
        # Small repulsion from obstacles-adjacent squares (deterministic).
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_pen += 2
        score -= adj_pen
        # If no resources, add preference to center.
        if not resources:
            score -= cheb(nx, ny, w // 2, h // 2)
        # Tie-break deterministically by dx,dy ordering already fixed; add exact coord tie.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]