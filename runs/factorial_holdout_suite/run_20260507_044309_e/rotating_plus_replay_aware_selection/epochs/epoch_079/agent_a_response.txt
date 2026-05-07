def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def best_adv(px, py):
        if not resources:
            tx, ty = w // 2, h // 2
            return 0, tx, ty, cheb(ox, oy, tx, ty), cheb(px, py, tx, ty)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive earlier; also value closeness and determinism.
            adv = do - ds
            row_bias = (ry <= oy) - (ry > oy)
            key = (adv, -ds, -row_bias, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry, do, ds)
        if best is None:
            tx, ty = w // 2, h // 2
            return 0, tx, ty, cheb(ox, oy, tx, ty), cheb(px, py, tx, ty)
        _, rx, ry, do, ds = best
        return (do - ds), rx, ry, do, ds

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        adv, rx, ry, do, ds = best_adv(nx, ny)
        # One-step lookahead: how much we reduce opponent threat to our chosen resource.
        # Use a proxy for "opponent pressure": after move, compare distances.
        opp_threat = do
        my_progress = ds
        # Prefer capturing-adjacent positions and avoid dead moves.
        near_cap = -1 if cheb(nx, ny, rx, ry) <= 1 else 0
        move_pen = 1 if (dx == 0 and dy == 0) else 0
        score = (adv, near_cap, -opp_threat, -my_progress, -move_pen, -rx, -ry)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]