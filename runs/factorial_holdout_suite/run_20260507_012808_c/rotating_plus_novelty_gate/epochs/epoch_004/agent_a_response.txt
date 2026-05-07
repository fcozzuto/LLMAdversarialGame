def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (ox, oy)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d = cheb(nx, ny, tx, ty)
            # also prefer moving toward board center slightly to avoid corner traps
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = cheb(nx, ny, cx, cy)
            key = (d, dc, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        best_key_for_res = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer taking a resource we can reach before opponent (lower ds-do),
            # while also keeping short distance from the candidate cell.
            adv = ds - do
            # If both are far, bias toward earlier overall by also using ds alone.
            key = (adv, ds, (rx + ry) & 7, rx, ry)
            if best_key_for_res is None or key < best_key_for_res:
                best_key_for_res = key

        # Additional penalty for stepping into cells that are "behind" obstacles relative to nearest resource.
        key_move = (best_key_for_res[0], best_key_for_res[1], best_key_for_res[2], nx, ny, dx, dy)
        if best_move is None or key_move < best_move[0]:
            best_move = (key_move, [dx, dy])

    if best_move is None:
        return [0, 0]
    return best_move[1]