def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    viable = [r for r in resources if (r[0], r[1]) not in obs]
    if not viable:
        # Move to farthest corner from opponent deterministically
        tx = 0 if (sx + (ox - sx)) >= (w - 1) else (w - 1)
        ty = 0 if (sy + (oy - sy)) >= (h - 1) else (h - 1)
        return [sgn(tx - sx), sgn(ty - sy)]

    best = None
    best_key = None
    for rx, ry in viable:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can contest (larger od-sd), then closer to us, then stable by coords
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    best_move = (0, 0)
    best_mkey = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        nd = cheb(nx, ny, tx, ty)

        # Penalize allowing opponent to be substantially closer to our target
        nod = cheb(ox, oy, tx, ty)
        gap_pen = nd - nod  # lower is better

        # Prefer moves that increase distance from opponent overall a bit (avoid direct contest)
        odist = cheb(nx, ny, ox, oy)

        # If target is on this move, strongly prefer it
        hit_bonus = -1000 if (nx == tx and ny == ty) else 0

        key = (nd, gap_pen, -odist, hit_bonus, dx, dy)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]