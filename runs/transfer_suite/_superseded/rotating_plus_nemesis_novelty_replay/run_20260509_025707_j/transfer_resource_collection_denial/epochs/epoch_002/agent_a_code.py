def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opts = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        # Prefer targets where we're at least as close; then maximize (we being closer); then closer absolute; then deterministic
        key = (0 if ds <= do else 1, -adv, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    cur_best_step = (0, 0)
    cur_best_key = None

    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate move by how it changes relative closeness to the chosen target and the best contested resource overall
        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Also consider immediate "next contested" resources: pick the best among a small deterministic subset (closest few)
        local_best_adv = None
        local_best_ds = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if local_best_adv is None or (-adv, ds, rx, ry) < (-local_best_adv, local_best_ds, rx, ry):
                local_best_adv = adv
                local_best_ds = ds
        contested_key = (0 if my_d <= opp_d else 1, -local_best_adv, my_d, nx, ny)
        if cur_best_key is None or contested_key < cur_best_key:
            cur_best_key = contested_key
            cur_best_step = (dx, dy)

    return [cur_best_step[0], cur_best_step[1]]