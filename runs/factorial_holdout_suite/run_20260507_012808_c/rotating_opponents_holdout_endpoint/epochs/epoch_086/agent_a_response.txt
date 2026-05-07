def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Drift toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            d = man(nx, ny, cx, cy)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose target resource with clear advantage; break ties deterministically.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds  # higher is better: we get there first
        edge_bias = 0
        if rx == 0 or rx == w - 1: edge_bias -= 0.05
        if ry == 0 or ry == h - 1: edge_bias -= 0.05
        # Prefer being earlier; slight preference for farther from opponent (to reduce immediate contests)
        key = (adv, -do, ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # One-step decision: avoid obstacles, prefer move that reduces our distance to target,
    # and if tied, reduces opponent advantage reversal (i.e., keeps adv non-decreasing).
    best = (0, 0)
    best_tuple = None
    cur_ds = man(sx, sy, tx, ty)
    cur_do = man(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns_ds = man(nx, ny, tx, ty)
        ns_do = man(ox, oy, tx, ty)  # opponent doesn't move this turn in our move delta
        adv = ns_do - ns_ds
        # Primary: reduce distance; Secondary: keep/raise adv; Tertiary deterministic tiebreak.
        tup = (-ns_ds, adv, -((abs(nx - ox) + abs(ny - oy)) ), nx, ny)
        if best_tuple is None or tup > best_tuple:
            best_tuple = tup
            best = (dx, dy)

    return [int(best[0]), int(best[1])]