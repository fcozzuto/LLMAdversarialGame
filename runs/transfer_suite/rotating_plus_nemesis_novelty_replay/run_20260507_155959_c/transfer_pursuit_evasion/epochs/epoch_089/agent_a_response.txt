def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")
    chase = (not self_evader) or opp_evader  # if we're not the evader, pursue; if opponent is evading, still chase

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def eval_move(nx, ny):
        dx, dy = nx - ox, ny - oy
        d2 = dx * dx + dy * dy
        man = abs(dx) + abs(dy)
        # obstacle proximity penalty to avoid getting boxed in
        prox = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                ax, ay = nx + adx, ny + ady
                if (ax, ay) in obs:
                    prox += 1
        # keep away from corners when chasing (improves escape paths) and toward corners when evading
        corner_dist = min(abs(nx - 0) + abs(ny - 0), abs(nx - (w - 1)) + abs(ny - 0),
                           abs(nx - 0) + abs(ny - (h - 1)), abs(nx - (w - 1)) + abs(ny - (h - 1)))
        center_bias = -corner_dist  # higher is better when center_dist is small; sign handled below

        if chase:
            # minimize distance to opponent; slight preference for center if equal
            return d2 + 0.2 * man + 3.0 * prox - 0.05 * corner_dist
        else:
            # maximize distance from opponent; prefer corners to herd into walls, but avoid obstacles
            return -d2 - 0.2 * man + 3.0 * prox + 0.02 * corner_dist

    best = None
    best_val = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        v = eval_move(nx, ny)
        if best_val is None or v < best_val if chase else v > best_val:
            best_val = v
            best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]