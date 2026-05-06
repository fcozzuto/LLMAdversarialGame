def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best = None
    # Denial-first: maximize lead (opponent distance - our distance) after our move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        best_res = None
        for rx, ry in resources:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            lead = opp_d - our_d
            # prefer large lead; when tied, smaller our distance; then stable resource order
            key = (-lead, our_d, rx, ry)
            if best_res is None or key < best_res[0]:
                best_res = (key, lead)
        lead_key, _ = best_res
        move_key = (lead_key, dx, dy)
        if best is None or move_key < best:
            best = move_key

    if best is None:
        return [0, 0]
    _, bx, by = best
    return [bx, by]