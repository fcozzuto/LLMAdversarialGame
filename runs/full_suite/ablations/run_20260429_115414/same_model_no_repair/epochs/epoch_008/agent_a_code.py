def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not dirs:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    # Strategic change: target resources by "grab priority" (opponent advantage), then evaluate moves with opponent-distance pressure.
    tx, ty = (w - 1, h - 1)
    if resources:
        best = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Prefer resources where we can beat opponent; tie-break by closeness to us, then determinism.
            key = (opd - myd, -(myd), -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Evaluate all legal moves; favor closing to target while keeping away from opponent (or at least not conceding ground).
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_to_t = dist(nx, ny, tx, ty)
        my_to_o = dist(nx, ny, ox, oy)
        o_to_t = dist(ox, oy, tx, ty)

        # If opponent is closer to target, prioritize blocking by increasing our distance from opponent and reducing their effective pressure.
        # If we are closer/equal, prioritize rapid capture by minimizing distance to target.
        myd_cur = dist(sx, sy, tx, ty)
        opd_cur = dist(ox, oy, tx, ty)
        if myd_cur <= opd_cur:
            # Aggressive: reduce my_to_t; keep moderate distance from opponent to avoid immediate contest loss.
            val = (-my_to_t, my_to_o, -abs(nx - sx) - abs(ny - sy))
        else:
            # Defensive/contest: increase distance from opponent and prevent them from improving too much toward target.
            val = (my_to_o, -(my_to_t - o_to_t), -abs(nx - tx) - abs(ny - ty))

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]