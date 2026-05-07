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

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            # Choose winning advantage first; then shorter ds; then deterministic position
            key = (-adv, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry), adv, ds, do)
        return best[1]

    tx, ty = best_target()
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_now = cheb(sx, sy, tx, ty)
        ds_next = cheb(nx, ny, tx, ty)
        # One-step look at advantage to discourage moves that concede the next resource
        do_next = cheb(ox, oy, tx, ty)
        # Value: primarily reduce our distance; secondarily increase (do - ds) advantage; slight bias toward deterministic progress
        val = (ds_next - ds_now, -(do_next - ds_next), abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]