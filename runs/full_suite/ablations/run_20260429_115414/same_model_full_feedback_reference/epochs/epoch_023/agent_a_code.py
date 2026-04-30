def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx + dy

    # Choose a target resource that we can reach relatively earlier than opponent.
    # If no resources visible, move to improve midline toward opponent side.
    if resources:
        best_r = resources[0]
        best_val = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Favor resources where opponent is further; slight bias toward closeness.
            val = (do - ds) * 10 - ds
            if best_val is None or val > best_val or (val == best_val and (rx, ry) < best_r):
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # Head toward a point closer to opponent (deny their approach) while staying safe.
        # Use a deterministic "aim" based on relative corner positions.
        tx, ty = (W - 1, H - 1) if (ox + oy) > (sx + sy) else (0, 0)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        # Primary: reduce our distance to target.
        ds = dist(nx, ny, tx, ty)
        do = dist(ox, oy, tx, ty)

        # Secondary: deny by increasing opponent's chance to take alternative nearby resources.
        # Approx: measure best (smallest) distance for opponent among a few candidate resources.
        opp_best = 10**9
        if resources:
            # deterministically iterate limited subset to keep small.
            # Sort-free: use simple index order as given.
            for rx, ry in resources:
                if (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy) <= 25:  # within ~5 steps squared
                    d = dist(ox, oy, rx, ry)
                    if d < opp_best:
                        opp_best = d
            if opp_best == 10**9:
                # fallback: use target
                opp_best = do

        # Tertiary: stay away from obstacles by preferring moves with more legal neighbors.
        free_neighbors = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if in_bounds(ax, ay):
                free_neighbors += 1

        score = (do - ds) * 10 - ds + (free_neighbors * 0.3) - (opp_best * 0.05)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]