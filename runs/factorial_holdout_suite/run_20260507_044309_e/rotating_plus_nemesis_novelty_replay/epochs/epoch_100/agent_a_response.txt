def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a "contested" target first: prioritize where we are relatively closer than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, -(rx * 100 + ry))  # maximize lead, then minimize ds, deterministic
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # If opponent is closer to all resources, pick the resource where we are closest (to reduce loss).
    mindiff = None
    best_self = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        diff = ds - do
        if mindiff is None or diff < mindiff:
            mindiff = diff
            best_self = (rx, ry)
    if mindiff < 0:
        # We are not losing on that contested target; keep it.
        pass
    else:
        tx, ty = best_self

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_m = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy  # engine may reject, keep deterministic evaluation

        ds_next = cheb(nx, ny, tx, ty)
        ds_now = cheb(sx, sy, tx, ty)
        # One-step advantage estimate around the chosen target.
        do_now = cheb(ox, oy, tx, ty)
        do_next = do_now  # opponent moves unknown; use current to stay deterministic

        # Encourage approaching target, discourage moving away, and slight preference to avoid obstacles.
        step_gain = (ds_now - ds_next)
        approach = -ds_next
        lead = do_next - ds_next

        avoid = 0
        for ax, ay in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            px, py = nx + ax, ny + ay
            if inb(px, py) and blocked(px, py):
                avoid -= 0.15

        val = 5.0 * lead + 1.5 * step_gain + 0.2 * approach + avoid
        if val > best_val:
            best_val = val
            best_m = [dx, dy]

    return best_m