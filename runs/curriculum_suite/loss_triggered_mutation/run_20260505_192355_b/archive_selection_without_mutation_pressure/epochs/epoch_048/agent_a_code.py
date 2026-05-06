def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_gap = -10**9
    best_res = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        gap = man(ox, oy, rx, ry) - man(sx, sy, rx, ry)
        if gap > best_gap:
            best_gap = gap
            best_res = (rx, ry)

    tx, ty = best_res
    if best_gap >= 0:
        # Take the advantage: minimize our distance, keep away from obstacles via ok()
        best = None
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Interception: try to reduce opponent progress to the best contested resource.
    # Use a deterministic tradeoff: prefer lower opp distance, then lower self distance.
    target = best_res
    tx, ty = target
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        # approximate "denial": after we move, opponent should be closer/farther to target.
        # Since we don't know opponent move, use current opp distance to target and weight by our proximity to opponent.
        base = -man(ox, oy, tx, ty)
        val = base + 0.35 * d_opp - 0.10 * man(nx, ny, tx, ty)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]