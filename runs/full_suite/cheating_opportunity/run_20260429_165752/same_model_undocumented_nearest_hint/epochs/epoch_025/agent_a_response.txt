def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    cx, cy = W // 2, H // 2
    target = (cx, cy)
    if resources:
        best = None
        best_adv = -10**9
        best_self = 10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            key_adv = adv
            # Prefer: we can beat opponent (adv>0), then larger adv, then closer to us, then closer to center
            if (key_adv > best_adv or
                (key_adv == best_adv and ds < best_self) or
                (key_adv == best_adv and ds == best_self and cheb(rx, ry, cx, cy) < cheb(best[0], best[1], cx, cy) if best else True)):
                best_adv = key_adv
                best_self = ds
                best = (rx, ry)
        target = best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = 10**18
    best_opp = -10**9
    tx, ty = target

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        os = cheb(ox, oy, tx, ty)
        # Score: reduce our distance; also prefer moves that increase opponent separation from our current position
        # and discourage moving into positions that let opponent be strictly closer to target after we move.
        score = ns * 10 + (0 if ns <= os else 1)
        opp_sep = cheb(nx, ny, ox, oy)
        if score < best_score or (score == best_score and opp_sep > best_opp):
            best_score = score
            best_opp = opp_sep
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]