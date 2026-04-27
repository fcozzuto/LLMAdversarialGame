def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((x, y) for x, y in obstacles)
    best_moves = []
    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
                continue
            d = max(abs(tx - nx), abs(ty - ny))
            val = -d
            if best is None or val > best[0]:
                best = (val, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    def cheb(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    # Prefer a move that closes on a resource where we are relatively closer than opponent.
    best_val = None
    best = (0, 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
            continue
        # Evaluate target resource
        cur_best = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Advantage: positive when we are closer (or equal) than opponent
            adv = od - sd
            # Also slightly penalize overall distance so we actually reach something
            val = adv * 10 - sd
            if cur_best is None or val > cur_best:
                cur_best = val
        # If no resources were reachable (shouldn't happen), keep still.
        if cur_best is None:
            cur_best = -10**9
        # Mild tie-break: avoid moving away from opponent to reduce interference chaos
        opp_tie = -cheb(nx, ny, ox, oy) * 0.01
        val2 = cur_best + opp_tie
        if best_val is None or val2 > best_val:
            best_val = val2
            best = (dx, dy)
    return [best[0], best[1]]