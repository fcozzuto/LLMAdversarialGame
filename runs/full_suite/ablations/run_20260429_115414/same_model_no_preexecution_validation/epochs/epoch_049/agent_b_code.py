def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: prioritize resources we can reach not worse than opponent; break ties by closer to opponent (deny).
    best_target = None
    best_tkey = None
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer: ds < do, then small ds, then large do (deny), then stable ordering.
        tkey = (0 if ds < do else 1, ds, -do, rx, ry)
        if best_tkey is None or tkey < best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    # If no resources, move to center-ish while keeping distance from opponent.
    if best_target is None:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_move = (0, 0)
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            ds_cent = -cheb(nx, ny, int(cx), int(cy))
            ds_opp = cheb(nx, ny, ox, oy)
            val = ds_cent + 0.25 * ds_opp
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = best_target

    # Local policy: maximize "gain" = reducing distance to target and increasing distance advantage over opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_now = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)  # opponent position static for this decision
        # Gain terms:
        #  - Strongly favor picking up/entering target
        #  - Prefer moves that keep or improve our relative reach (ds_now vs do_now)
        #  - If contested, also push away from opponent to reduce their ability to contest our future route
        pick = 1000 if (nx == tx and ny == ty) else 0
        rel = (do_now - ds_now)  # higher is better for us
        rel_bias = 10 * rel
        # Small tie-break: closer to target; and keep distance from opponent
        dist_t = -ds_now
        dist_o = 0.1 * cheb(nx, ny, ox, oy)
        # Penalize stepping adjacent to obstacle? (lightweight, deterministic)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1
        val = pick + rel_bias + dist_t +