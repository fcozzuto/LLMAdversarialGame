def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_raw if p and len(p) >= 2}
    resources = [(p[0], p[1]) for p in res if p and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # Safe drift toward center-ish
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            risk = 0
            for kx in (-1, 0, 1):
                for ky in (-1, 0, 1):
                    if kx == 0 and ky == 0:
                        continue
                    if (nx + kx, ny + ky) in obstacles:
                        risk += 1
            v = (man(nx, ny, tx, ty), risk, nx, ny)
            if v < best:
                best = (v[0], v[1], dx, dy)
        return [best[2], best[3]]

    # Prefer immediate collection, then maximize advantage over opponent for chosen target
    res_set = set(resources)
    best = (-(10**9), 10**9, 0, 0)  # (adv, opp_dist, dx, dy); higher adv, lower opp_dist
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        risk = 0
        for kx in (-1, 0, 1):
            for ky in (-1, 0, 1):
                if kx == 0 and ky == 0:
                    continue
                if (nx + kx, ny + ky) in obstacles:
                    risk += 1

        if (nx, ny) in res_set:
            # Guaranteed immediate pickup (deterministic strongest preference)
            best = (10**9 - risk, 0, dx, dy)
            continue

        # Evaluate top few resources by our closeness (deterministic pruning)
        # Sort by our distance, then by coordinates to keep deterministic.
        candidates = sorted(resources, key=lambda p: (man(nx, ny, p[0], p[1]), p[0], p[1]))[:5]
        local_best_adv = -10**9
        local_best_oppdist = 10**9
        for rx, ry in candidates:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Adv: we want opponent farther than us; also value fast collection
            adv = (do - ds) * 100 - ds - risk * 2
            if adv > local_best_adv or (adv == local_best_adv and do < local_best_oppdist):
                local_best_adv = adv
                local_best_oppdist = do

        v = (local_best_adv, local_best_oppdist, dx, dy)
        if v[0] > best[0] or (v[0] == best[0] and v[1] < best[1]):
            best = (v[0], v[1], v[2], v[3])

    return [best[2], best[3]]