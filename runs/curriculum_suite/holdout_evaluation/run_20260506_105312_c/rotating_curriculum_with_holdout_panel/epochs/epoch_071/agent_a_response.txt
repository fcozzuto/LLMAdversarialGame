def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no resources, drift toward center to reduce being pinned.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            key = (man(nx, ny, cx, cy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    rpos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rpos.append((int(r[0]), int(r[1])))

    # Try to secure nearest resource while denier-arena: also reduce opponent's access.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_near = 10**9
        opp_near = 10**9
        my_best = None
        opp_best = None
        for rx, ry in rpos:
            dm = man(nx, ny, rx, ry)
            if dm < my_near or (dm == my_near and (rx, ry) < (my_best or (10**9, 10**9))):
                my_near = dm
                my_best = (rx, ry)
            do = man(ox, oy, rx, ry)
            if do < opp_near or (do == opp_near and (rx, ry) < (opp_best or (10**9, 10**9))):
                opp_near = do
                opp_best = (rx, ry)

        # Predict opponent's next step too (deterministically assume same move-choice heuristic).
        # Compute best move for opponent from their position against our move: approximate their best access.
        opp_best_after = 10**9
        for odx, ody in moves:
            ex, ey = ox + odx, oy + ody
            if not inb(ex, ey) or (ex, ey) in obs:
                continue
            near = 10**9
            for rx, ry in rpos:
                d = man(ex, ey, rx, ry)
                if d < near:
                    near = d
            if near < opp_best_after:
                opp_best_after = near

        # Reward: shorter my distance, penalize opponent access, add small preference toward our chosen target direction.
        # Also slightly prefer moves that increase separation from opponent (denier games benefit from distance).
        sep = man(nx, ny, ox, oy)
        key = (
            my_near * 3 + opp_best_after * 2 - sep * 0.2,
            my_near,
            -sep,
            dx,
            dy
        )

        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]