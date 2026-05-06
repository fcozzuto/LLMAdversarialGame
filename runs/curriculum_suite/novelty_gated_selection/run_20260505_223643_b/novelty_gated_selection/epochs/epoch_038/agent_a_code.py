def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Choose a target that is relatively closer to us, but farther for the opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        oppd = manh(ox, oy, rx, ry)
        # Minimize: our distance + 2*(opponent distance) with tie-break favoring larger oppd.
        key = (myd + 2 * oppd, myd, -oppd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate next step: prioritize moving toward target while keeping opponent far.
    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd2 = manh(nx, ny, tx, ty)
        oppd2 = manh(ox, oy, tx, ty)
        # If we can potentially reach target sooner than opponent, boost.
        myd_now = manh(sx, sy, tx, ty)
        oppd_now = manh(ox, oy, tx, ty)
        # Denial: also consider increasing opponent distance from our current-to-target line via oppd2.
        reachable = 1 if myd2 <= oppd2 else 0
        eval_key = (myd2 + 2 * oppd2 - 3 * reachable, myd2, -oppd2, dx, dy, nx, ny)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    dx, dy = best_move
    # If all candidate moves were blocked/invalid, fall back to staying.
    return [dx, dy]