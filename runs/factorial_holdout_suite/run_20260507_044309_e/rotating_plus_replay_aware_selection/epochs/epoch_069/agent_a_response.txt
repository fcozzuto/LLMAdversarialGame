def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resources where we are at least as close as opponent; otherwise best "steal potential".
    def target_for(posx, posy):
        if not resources:
            return (w // 2, h // 2)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d1 = cheb(posx, posy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Priority: being closer or tying; then minimize our distance; then maximize closeness gap (we want d2-d1 big)
            # If all are worse (d1>d2), still choose one with best steal potential (largest d2-d1), then closest ours.
            gap = d2 - d1
            key = (0 if d1 <= d2 else 1, d1, -gap, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1]

    tx, ty = target_for(sx, sy)
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        cur_tx, cur_ty = target_for(nx, ny)
        d_me = cheb(nx, ny, cur_tx, cur_ty)
        d_opp = cheb(ox, oy, cur_tx, cur_ty)
        dist_to_target = cheb(nx, ny, tx, ty)
        # Prefer reducing distance to a strong target and winning the race to it.
        key = (-(1 if d_me <= d_opp else 0), d_me, -(d_opp - d_me), dist_to_target, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]