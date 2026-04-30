def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid_cell(x, y):
        return inside(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid_cell(x, y):
                res_cells.append((x, y))

    if not res_cells:
        # fallback: head toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid_cell(nx, ny):
                continue
            # prefer smaller distance
            v = -max(abs(nx - cx), abs(ny - cy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Prefer moves that (a) make us relatively closer than opponent to a resource
    # and (b) reduce opponent's closeness to that same resource (blocking effect).
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = -10**18
    # Tie-break deterministic order: keep first best in moves list.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid_cell(nx, ny):
            continue
        # For this hypothetical next position, evaluate the best "target" resource.
        # Score: maximize (opp_dist - my_dist). If tie, minimize my_dist.
        # Add small extra preference for targets we can reach no later than opponent.
        local_best = -10**18
        local_my = 10**9
        for tx, ty in res_cells:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            diff = opd - myd
            # Reward being at least as good as opponent; penalize if we trail.
            ahead_bonus = 2 if myd <= opd else 0
            # Main: diff, then smaller myd, then larger opd (slower opponent access)
            score = diff * 1000 + ahead_bonus * 10 - myd + (opd - myd)
            if score > local_best or (score == local_best and myd < local_my):
                local_best = score
                local_my = myd
        # Small penalty for staying still unless it is already the best option.
        stay_pen = 1 if (dxm == 0 and dym == 0) else 0
        total_score = local_best - stay_pen
        if total_score > best_score:
            best_score = total_score
            best_move = [dxm, dym]

    return best_move