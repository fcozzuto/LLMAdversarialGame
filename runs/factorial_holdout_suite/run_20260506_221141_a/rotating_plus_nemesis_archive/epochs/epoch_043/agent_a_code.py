def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        by = b - d
        if by < 0: by = -by
        return ax if ax >= by else by

    best = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        adv = od - sd
        # tie-break: prefer closer to self; then prefer cell closer to center
        center = abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0)
        cand = (adv, -sd, -center)
        if best is None or cand > best[0]:
            best = (cand, (x, y))

    tx, ty = best[1]
    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Encourage moves that preserve advantage; slight bias toward reducing distance
        val = (nod - nsd, -nsd, -abs(nx - tx) - abs(ny - ty))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If all moves blocked (rare), stay.
    return best_move