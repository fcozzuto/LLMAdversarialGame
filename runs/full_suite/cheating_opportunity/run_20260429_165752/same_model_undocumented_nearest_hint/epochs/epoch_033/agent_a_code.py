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

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def obs_adj_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2
        return pen

    # Pick a deterministic "best" target resource we are relatively closer to.
    if resources:
        best = None
        best_score = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive sooner; break ties by being closer.
            score = (d_op - d_me) * 10 - d_me
            if score > best_score or (score == best_score and (d_me < (cheb(sx, sy, best[0], best[1]) if best else 10**9))):
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources visible: move toward center to keep options open.
        tx, ty = W // 2, H // 2

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Encourage reducing distance to target while staying ahead of opponent, but don't hug obstacles.
        val = -d_me * 3 + (d_op - d_me) * 4 - obs_adj_pen(nx, ny) * 1
        # If opponent is very close to target, try to get in front of it.
        if resources:
            opp_to_target = cheb(ox, oy, tx, ty)
            if opp_to_target <= d_me + 1:
                val += 5
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move