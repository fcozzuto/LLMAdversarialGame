def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                if 0 <= x < w and 0 <= y < h:
                    obs_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Evaluate each possible move by best resource we can "beat" after moving
    best_move = [0, 0]
    best_val = None
    for dxm in (-1, 0, 1):
        for dym in (-1, 0, 1):
            nx, ny = sx + dxm, sy + dym
            if not inb(nx, ny):
                continue
            penalty = -1000 if (nx, ny) in obs_set else 0
            # If landing on obstacle, engine will keep us in place; emulate by strong penalty
            if (nx, ny) in obs_set:
                nx, ny = sx, sy
            our_best = None
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                tx, ty = r[0], r[1]
                if not (isinstance(tx, int) and isinstance(ty, int) and inb(tx, ty)):
                    continue
                sd = cheb(nx, ny, tx, ty)
                od = cheb(ox, oy, tx, ty)
                adv = od - sd  # positive => we arrive earlier (or same if 0)
                # Prefer earlier arrival; if we can't beat, still prefer reducing our delay relative to opponent
                val = (adv * 100) - sd
                if our_best is None or val > our_best:
                    our_best = val
            if our_best is None:
                our_best = -cheb(nx, ny, ox, oy)  # fallback: move away from opponent
            total = penalty + our_best
            key = (-total, dxm, dym)
            if best_val is None or key < best_val:
                best_val = key
                best_move = [dxm, dym]
    return [int(best_move[0]), int(best_move[1])]