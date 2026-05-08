def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    # Target: resource where we are relatively closer; else best fallback.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        diff = opp_d - our_d  # positive is good for us
        # Prefer positive diff; then minimize our_d; then maximize diff; then stable by coords
        key = (0 if diff >= 0 else 1, -diff, our_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    deltas = [(dx, dy) for dy in dys for dx in dxs if not (dx == 0 and dy == 0)]
    deltas.append((0, 0))  # stay last to prefer movement

    # Move choice: follow target but avoid obstacles and keep advantage increasing.
    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            return (10**9, 10**9, 10**9, 10**9)
        if (nx, ny) in obstacles:
            return (10**8, 10**8, 10**8, 10**8)
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        adv = opp_d - our_d
        # Also softly prefer moves that reduce distance to target and improve relative to opponent.
        return (-1 if adv >= 0 else 0, -adv, our_d, abs(nx - tx) + abs(ny - ty))

    best_m = None
    best_key = None
    for dx, dy in deltas:
        k = score_move(dx, dy)
        if best_key is None or k < best_key:
            best_key = k
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]