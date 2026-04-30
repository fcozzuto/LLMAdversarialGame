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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # New strategy: choose a resource where we can gain the largest distance advantage over the opponent.
    # Score = (opponent distance - my distance) - small penalty for being far ourselves.
    best_t = None
    best_s = -10**9
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        margin = opd - myd
        center_bias = -0.03 * (abs(tx - cx) + abs(ty - cy))
        s = margin - 0.08 * myd + center_bias
        if s > best_s:
            best_s = s
            best_t = (tx, ty)

    tx, ty = best_t
    # Move by maximizing improvement toward target while keeping away from opponent (avoid getting contested too tightly).
    bestm = (0, 0, -10**9)
    cur_to_t = cheb(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        to_t = cheb(nx, ny, tx, ty)
        to_o = cheb(nx, ny, ox, oy)
        gain = cur_to_t - to_t
        # If opponent is closer to the target than we are, prioritize increasing distance margin.
        opp_to_t = cheb(ox, oy, tx, ty)
        my_margin = opp_to_t - to_t
        score = 3.0 * gain + 0.06 * to_o + 0.8 * my_margin
        if score > bestm[2]:
            bestm = (dx, dy, score)

    return [bestm[0], bestm[1]]