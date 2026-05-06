def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

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

    if not resources:
        return [0, 0]

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_key = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_gain = None
        best_dself = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            dself = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            gain = dop - dself
            if best_gain is None or gain > best_gain or (gain == best_gain and dself < best_dself) or (
                gain == best_gain and dself == best_dself and (rx + ry) < (best_rx + best_ry)
            ):
                best_gain = gain
                best_dself = dself
                best_rx, best_ry = rx, ry

        # Prefer immediate resource capture (gain highest and dself smallest),
        # break ties deterministically toward smaller coordinates.
        key = (best_gain, -best_dself, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]