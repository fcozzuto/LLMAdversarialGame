def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            # Prefer larger advantage; then closer to resource; then lexicographic
            key = (-adv, myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = W - 1, H - 1  # deterministic fallback

    my_to_t = cheb(sx, sy, tx, ty)
    op_to_t = cheb(ox, oy, tx, ty)
    contested = op_to_t < my_to_t

    def obstacle_penalty(x, y):
        # penalize being adjacent to obstacles (encourages route around them)
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    pen += 2
        if (x, y) in obstacles:
            pen += 50
        return pen

    best_move = (0, 0)
    best_score = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue
        pen = obstacle_penalty(nx, ny)

        nd_my = cheb(nx, ny, tx, ty)
        # opponent position unchanged this step; still valuable for contesting
        nd_op = op_to_t

        # Base: get closer to target; also reduce opponent's relative access (via my distance only)
        score = (my_to_t - nd_my) * 3 - pen

        # If opponent is already closer to the target, switch to defensive/denial: increase distance to opponent
        if contested:
            score += cheb(nx, ny, ox, oy) * 0.8

        # If not contested, slightly encourage moves that also increase distance from opponent (avoid early steal)
        if not contested:
            score += cheb(nx, ny, ox, oy) * 0.2

        # Tie-break deterministically: lexicographic on move
        key = (-score, nd_my, nx, ny, dxm, dym)
        best_key