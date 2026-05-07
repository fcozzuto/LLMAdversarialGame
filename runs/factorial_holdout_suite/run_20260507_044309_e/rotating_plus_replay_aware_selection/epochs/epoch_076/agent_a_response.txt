def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_res = None
    best_key = None
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive means we can beat them
            # Tie-break: prefer resources we can beat; if close, prefer those higher value (by proximity to center) and more "front" (toward opponent)
            center = cheb(rx, ry, w // 2, h // 2)
            front = (rx - ox) if ox <= sx else (ox - rx)
            key = (margin, -ds, -center, front, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)

    # If no good resource (or none), go to a "relay" point between both agents to reduce their denial tempo.
    if best_res is None:
        tx = (sx + ox) // 2
        ty = (sy + oy) // 2
    else:
        tx, ty = best_res

    # Evaluate candidate moves by their impact on beating the chosen target and denying opponent (move toward target while increasing opponent distance).
    chosen_dxdy = (0, 0)
    chosen_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_next = cheb(nx, ny, tx, ty)
        do_next = cheb(ox, oy, tx, ty)
        margin_next = do_next - ds_next
        # Also add slight step penalty to discourage dithering; and small improvement if we reduce opponent reach to any resource near us.
        step_pen = ds_next * 0.001
        score = (margin_next, -ds_next, -step_pen, -cheb(ox, oy, tx, ty))
        if chosen_score is None or score > chosen_score:
            chosen_score = score
            chosen_dxdy = (dx, dy)

    return [int(chosen_dxdy[0]), int(chosen_dxdy[1])]