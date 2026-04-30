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
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if resources:
        # Choose resource we are closest to relative to opponent.
        best_r = None
        best_v = None
        for tx, ty in resources:
            dm = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer wins: positive (do-dm); tie-break nearer to us; then lower coords.
            v = (do - dm)
            if best_v is None or v > best_v or (v == best_v and (dm < cheb(sx, sy, best_r[0], best_r[1]) or (dm == cheb(sx, sy, best_r[0], best_r[1]) and (tx, ty) < best_r))):
                best_v = v
                best_r = (tx, ty)
        tx, ty = best_r
    else:
        tx, ty = W // 2, H // 2

    # Evaluate each move: maximize advantage to chosen target; lightly penalize stepping into opponent range.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dm_now = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        # Encourage moving to reduce our remaining distance faster than opponent.
        score = (do_now - dm_now) * 100 - dm_now
        # If opponent is extremely close to the target, prioritize extra distance from opponent path direction.
        opp_close = cheb(ox, oy, tx, ty)
        score += (4 - opp_close) * 3
        # Tie-break deterministically: prefer smaller (dx,dy) ordering bias.
        score += -(abs(dx) * 0.01 + abs(dy) * 0.01)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]