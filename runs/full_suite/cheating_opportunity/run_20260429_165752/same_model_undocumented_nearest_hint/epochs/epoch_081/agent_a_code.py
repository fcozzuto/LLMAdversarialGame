def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [W - 1, H - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        tx, ty = (W // 2), (H // 2)
        best = (0, 0)
        bd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bd:
                bd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    opp_dist_to_center = cheb(ox, oy, (W - 1) / 2.0, (H - 1) / 2.0)

    best_move = (0, 0)
    best_val = -10**18
    # Prefer moves that maximize "take-advantage": resources where we can arrive much sooner than opponent.
    # Also slightly prefer moving toward those advantaged resources (and away from letting opponent get tempo).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_d = cheb(nx, ny, sx, sy)
        val = -0.03 * my_d  # tiny regularizer to reduce dithering
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we're closer after this move
            # Emphasize immediate competitive advantage; penalize being the one farther.
            cand = 2.0 * adv - 0.25 * ds
            # Tie-break without randomness: slight bias to resources more "toward our side" when adv similar.
            center_bias = 0.001 * (-(abs(rx - (W * 0.0 + 0.0)) + abs(ry - (H * 0.0 + 0.0))))
            # If opponent is currently very central, reduce chance of long contested detours.
            tempo_pen = 0.001 * (do + opp_dist_to_center)
            score = cand + center_bias - tempo_pen
            if score > val:
                val = score
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]