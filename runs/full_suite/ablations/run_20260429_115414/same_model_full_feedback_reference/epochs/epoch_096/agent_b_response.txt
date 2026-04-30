def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not legal(sx, sy):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach sooner; slight bias away from staying too close to opponent
        lead = do - ds
        center_bias = 0
        cx, cy = W / 2.0, H / 2.0
        dist_center = cheb(tx, ty, int(cx), int(cy))
        center_bias = -0.02 * dist_center
        return 1000 * lead + center_bias

    # If no visible resources, go to a safer "interference" zone: move away from opponent while staying toward center
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        best = None
        best_val = None
        for tx, ty in resources:
            v = score_target(tx, ty)
            if best is None or v > best_val or (v == best_val and (cheb(sx, sy, tx, ty) < cheb(sx, sy, best[0], best[1]))):
                best = (tx, ty)
                best_val = v
        tx, ty = best
    else:
        tx, ty = int(W / 2), int(H / 2)

    # Local greedy step: move toward target, but if opponent is closer to target, emphasize increasing opponent distance
    prefer_away = 1 if cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty) else 0

    best_move = [0, 0]
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Evaluate: primarily reduce distance to target; secondarily maximize distance to opponent; tertiary avoid obstacles indirectly by prefer larger move distance to their current location
        t = (d_to_target, -d_to_opp if prefer_away else d_to_opp)
        if best_tuple is None or t < best_tuple:
            best_tuple = t
            best_move = [dx, dy]

    return best_move