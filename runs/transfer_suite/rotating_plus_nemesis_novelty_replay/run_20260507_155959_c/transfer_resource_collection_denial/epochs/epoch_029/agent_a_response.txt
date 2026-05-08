def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = []
    for r in resources:
        rx, ry = r[0], r[1]
        if inb(rx, ry) and (rx, ry) not in obs:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = -10**18

    # Anticipatory target: prefer resources where we can get advantage over the opponent.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = -10**18
        best_r = None
        for rx, ry in res:
            da = md(nx, ny, rx, ry)
            db = md(ox, oy, rx, ry)
            adv = db - da  # positive => we are closer than opponent
            # If we cannot beat them on a resource now, still consider contesting the one closest to becoming winnable.
            key = (adv, -da, -abs(rx - ox) - abs(ry - oy))
            if key > (best_adv, -10**18, -10**18):
                best_adv = adv
                best_r = (rx, ry)
        rx, ry = best_r

        # Main value: maximize winning advantage; tie-break by moving closer.
        da = md(nx, ny, rx, ry)
        db = md(ox, oy, rx, ry)
        val = 15 * (db - da) - da

        # Secondary: reduce distance to all resources slightly (prevents dithering near corner).
        min_da = 10**9
        for (tx, ty) in res:
            d = md(nx, ny, tx, ty)
            if d < min_da:
                min_da = d
        val -= 0.3 * min_da

        # Small bias to avoid getting stuck behind obstacles: prefer moves that increase reachable Y progress.
        val += 0.02 * (ny - sy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]