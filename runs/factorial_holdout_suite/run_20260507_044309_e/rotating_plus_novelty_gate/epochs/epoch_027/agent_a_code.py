def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    valid_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    # Grab if adjacent
    for dx, dy, nx, ny in valid_moves:
        for rx, ry in resources:
            if nx == rx and ny == ry:
                return [dx, dy]

    # Choose a target resource where we can beat opponent (or at least not lose badly),
    # then move one step that minimizes our distance to that target and maximizes contest margin.
    best = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # contest_score: higher is better. If we can reach earlier, strongly prefer.
        contest = (do - ds)  # positive means we are closer
        score = contest * 10 - ds  # prefer earlier/closer but keep contest primary
        if best is None or score > best[0]:
            best = (score, rx, ry, ds, do)

    if best is None:
        return [0, 0]
    _, tx, ty, _, _ = best

    # Secondary: if our target is far, keep moving "toward the center band" in y to avoid sweep-row trapping.
    center_band = (h // 2, h // 2 + 1)

    best_move = None
    best_val = None
    for dx, dy, nx, ny in valid_moves:
        # Compute contest margin if we move here (one-step look)
        ds_next = manh(nx, ny, tx, ty)
        do_here = manh(ox, oy, tx, ty)
        val = (do_here - ds_next) * 10 - ds_next

        # Obstacle-aware soft bias: prefer moves that change y toward middle band when not adjacent to target
        if manh(sx, sy, tx, ty) > 3:
            cy = center_band[0] if abs(ny - center_band[0]) <= abs(ny - center_band[1]) else center_band[1]
            val += -abs(ny - cy)  # closer to band is better
            # Also gently prefer advancing y if opponent is sweeping (unknown), but keep deterministic
            val += (1 if ny > sy else (-1 if ny < sy else 0))

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then stay
        tie = (0 if dx == 0 else 1, 0 if dy == 0 else 1, abs(dx), abs(dy))
        if best_val is None or val > best_val or (val == best_val and tie < best_move[0]):
            best_val = val
            best_move = (tie, dx, dy)

    return [best_move[1], best_move[2]]