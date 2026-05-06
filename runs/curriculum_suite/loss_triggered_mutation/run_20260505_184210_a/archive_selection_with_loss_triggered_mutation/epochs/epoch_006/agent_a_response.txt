def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list)
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    def step_options(cx, cy):
        opts = []
        for dx, dy in deltas:
            nx, ny = cx + dx, cy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            opts.append((nx, ny, dx, dy))
        if not opts:
            return [(cx, cy, 0, 0)]
        return opts

    # Target: pick resource maximizing arrival advantage (prefer we are earlier), else contest closest.
    tx, ty = sx, sy
    if resources:
        best = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # primary: earlier arrival for us; secondary: minimize our distance; tertiary: minimize opponent distance
            primary = (do - ds)  # larger is better
            tie = (ds, do, abs(rx - (w-1)/2) + abs(ry - (h-1)/2))
            cand = (primary, -tie[1], tie)  # deterministic ordering
            if best is None or cand > best[0]:
                best = (cand, (rx, ry))
        tx, ty = best[1]
    else:
        # No visible resources: head to a safe midpoint but bias upward/diagonal to disrupt edge_patrol.
        tx = (sx + ox) // 2
        ty = (sy + oy) // 2
        if (ty + sx) % 2 == 0:
            tx = max(0, min(w-1, tx + (1 if sx < ox else -1)))
        else:
            ty = max(0, min(h-1, ty + (1 if sy < oy else -1)))

    # If target cell is blocked, try nearby deterministic fallbacks.
    if (tx, ty) in obstacles:
        fallback = [(tx, ty), ((tx+sx)//2, (ty+sy)//2), (sx, sy), (tx, max(0, min(h-1, ty-1))), (max(0, min(w-1, tx-1)), ty)]
        for fx, fy in fallback:
            if inb(fx, fy) and (fx, fy) not in obstacles:
                tx, ty = fx, fy
                break

    opts = step_options(sx, sy)
    # Opponent-aware: also keep us away from being directly outflanked; prefer moves that reduce distance to target.
    scored = []
    for nx, ny, dx, dy in opts:
        ns = dist((nx, ny), (tx, ty))
        no = dist((nx, ny), (ox, oy))
        ds_after = dist((sx, sy), (tx, ty))
        do_after = dist((ox, oy), (tx, ty))
        # Estimated advantage if we move: reduce our target distance and avoid giving opponent a closer access.
        est_adv = (do_after - ns)  # higher better
        # Small bias to break ties: prefer forward-ish (toward increasing x if we started left, else decreasing)
        forward_bias = (nx - sx) * (1 if sx <= (w-1)/2 else -1) + (ny - sy) * (1 if sy <= (h-1)/2 else -1)
        obstacle_pen = 0
        scored.append((est_adv, -ns, no, forward_bias, dx, dy, obstacle_pen))
    scored.sort(reverse=True)
    _, _, _, _, dx, dy, _ = scored[0]
    return [int(dx), int(dy)]