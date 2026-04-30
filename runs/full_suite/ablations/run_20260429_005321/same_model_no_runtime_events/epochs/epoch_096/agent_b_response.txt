def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [w - 1, h - 1]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if d > bestv:
                bestv = d
                best = (dx, dy)
        return [best[0], best[1]]

    def manh(ax, ay, bx, by):
        ax = ax - bx
        ay = ay - by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    # Pick a target resource where we maximize distance advantage over opponent.
    best_r = resources[0]
    best_adv = -10**18
    best_ds = 10**9
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and ds < best_ds):
            best_adv, best_ds, best_r = adv, ds, (rx, ry)

    tx, ty = best_r

    # Move selection: maximize immediate gain in distance advantage, while keeping distance from opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = manh(nx, ny, tx, ty)
        do2 = manh(ox, oy, tx, ty)
        adv2 = do2 - ds2

        # Chebyshev-ish separation penalty (squared distance)
        sep2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Prefer getting closer to target even if opponent also close
        target_closer = best_ds - ds2

        val = adv2 * 1000 + target_closer * 10 + sep2 * 0.05
        # Slightly avoid ending adjacent to opponent if we don't improve target advantage
        if manh(nx, ny, ox, oy) <= 1 and adv2 <= best_adv:
            val -= 50

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]