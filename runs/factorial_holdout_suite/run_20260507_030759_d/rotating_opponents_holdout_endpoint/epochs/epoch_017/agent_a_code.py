def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def clamp_step(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            # fallback: axis step
            if dx != 0 and inb(sx + dx, sy) and (sx + dx, sy) not in oset:
                return [dx, 0]
            if dy != 0 and inb(sx, sy + dy) and (sx, sy + dy) not in oset:
                return [0, dy]
            return [0, 0]
        return [dx, dy]

    best = None
    best_key = None
    best_margin = -10**9

    # Key: primary deny/win margin (opp closer -> negative), secondary prefer nearer to self,
    # tertiary prefer farther from opponent when margins tie.
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int) and inb(rx, ry)):
            continue
        if (rx, ry) in oset:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        margin = do - ds
        # Higher is better:
        key = (
            margin,
            -ds,
            do,
            -abs(rx - (sx + ox) // 2) - abs(ry - (sy + oy) // 2)
        )
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
            best_margin = margin

    if best is None:
        # No reachable resources; just move toward opponent's corner line deterministically.
        tx, ty = ox, oy
        return clamp_step(tx, ty)

    # If opponent is clearly closer to all (margin <= 0), switch to minimizing ds (best chance to still grab one).
    if best_margin <= 0:
        closest = None
        closest_d = 10**9
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                if isinstance(rx, int) and isinstance(ry, int) and inb(rx, ry) and (rx, ry) not in oset:
                    ds = abs(rx - sx) + abs(ry - sy)
                    if ds < closest_d or (ds == closest_d and (ox * 3 + oy) % 2 == 0):
                        closest_d = ds
                        closest = (rx, ry)
        if closest is not None:
            best = closest

    return clamp_step(best[0], best[1])