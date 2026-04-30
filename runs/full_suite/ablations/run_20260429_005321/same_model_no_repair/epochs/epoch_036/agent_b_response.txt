def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    if not resources:
        return [0, 0]

    # Pick a target resource that maximizes current "lead" (we are closer).
    best_rx, best_ry = None, None
    best_lead = -10**9
    best_ds = 10**9
    cx = (gw - 1) / 2.0
    cy = (gh - 1) / 2.0
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = do - ds
        # small center bias to break ties deterministically
        center = -0.001 * ((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        if lead > best_lead or (lead == best_lead and (ds < best_ds or (ds == best_ds and center > 0))):
            best_lead = lead
            best_ds = ds
            best_rx, best_ry = rx, ry

    if best_rx is None:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_d = man(nx, ny, best_rx, best_ry)
        op_d = man(ox, oy, best_rx, best_ry)
        lead_after = op_d - my_d  # positive => still closer than opponent
        # Also slightly reward approaching the most contested resource (closest to opponent).
        cont_d = None
        cont = None
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            do = man(ox, oy, rx, ry)
            if cont_d is None or do < cont_d or (do == cont_d and man(sx, sy, rx, ry) < man(sx, sy, cont[0], cont[1])):
                cont_d = do
                cont = (rx, ry)
        contested_bias = 0.0
        if cont is not None:
            contested_bias = -0.1 * man(nx, ny, cont[0], cont[1])

        score = lead_after * 1000 - my_d * 2 + contested_bias + (dx * 0 + dy * 0)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]