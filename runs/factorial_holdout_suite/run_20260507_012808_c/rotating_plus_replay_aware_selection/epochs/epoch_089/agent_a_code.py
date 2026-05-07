def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        best = [0, 0]
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_self = cheb(nx, ny, tx, ty)
            d_opp_now = cheb(ox, oy, tx, ty)
            d_opp_after = d_opp_now  # opponent move unknown; proxy via our move quality only
            # Prefer reducing self distance; slightly reward moves that increase own "tempo" (avoid stagnation)
            score = (d_opp_after - d_self) * 100 - d_self + (1 if (dx != 0 or dy != 0) else 0)
            if score > best_score:
                best_score = score
                best = [dx, dy]
        return best

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return step_toward(tx, ty)

    # Choose a target resource where we are at least as close as opponent (or closest available).
    best_target = None
    best_margin = -10**18
    for rx, ry in resources:
        if not valid(rx, ry):
            continue
        d_s = cheb(sx, sy, rx, ry)
        d_o = cheb(ox, oy, rx, ry)
        margin = d_o - d_s  # positive means we are closer
        # tie-break toward smaller d_s and then toward top-left deterministic ordering
        key = (margin, -d_s, -rx, -ry)
        if best_target is None or key > best_margin:
            best_margin = key
            best_target = (rx, ry)

    if best_target is None:
        # All resources invalid (unlikely); just move to center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return step_toward(tx, ty)

    tx, ty = best_target
    # If we're already on/adjacent to target, prioritize capturing by moving directly onto it when possible.
    best = [0, 0]
    bestd = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Strictly prefer minimum distance; tie-break by reducing opponent advantage proxy (our closeness)
        score = (-d, -(abs(nx - tx) + abs(ny - ty)), (0 if (dx == 0 and dy == 0) else 1))
        if d < bestd or (d == bestd and score > (-bestd, 0, 0)):
            bestd = d
            best = [dx, dy]
    return best