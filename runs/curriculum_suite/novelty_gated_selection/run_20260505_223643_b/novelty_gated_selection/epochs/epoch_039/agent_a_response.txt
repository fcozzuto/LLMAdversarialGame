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

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def clamp_in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a global target, but later move-scoring will decide the step.
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        oppd = manh(ox, oy, rx, ry)
        # Prefer being closer while keeping opponent far; slight bias to more "reachable" cells.
        key = (myd + 2 * oppd, myd - 0.01 * oppd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in_bounds(nx, ny):
            continue

        # Self progress to target
        self_to = manh(nx, ny, tx, ty)
        # Also consider whether this move improves our lead on the best nearby resource
        local_best = None
        for rx, ry in resources:
            d1 = manh(nx, ny, rx, ry)
            d2 = manh(ox, oy, rx, ry)
            k = (d1 + 2 * d2, d1, -d2)
            if local_best is None or k < local_best:
                local_best = k
        _, d1min, _ = local_best

        # Interference: avoid moving into opponent-favorable proximity
        opp_prox = manh(nx, ny, ox, oy)

        # Reward settling onto resources, discourage proximity to opponent when contested
        on_res = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0
        contested = 1 if (manh(ox, oy, tx, ty) <= self_to + 1) else 0

        val = (-self_to, -d1min, -opp_prox, on_res, -contested)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]