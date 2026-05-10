def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Target: where we arrive earlier than opponent (maximize advantage), then closer.
    best_key = None
    best_t = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # larger is better
        key = (-adv, sd, ry, rx)  # minimize negative advantage => maximize advantage
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t

    # Choose best move among neighbors toward that target, avoiding obstacles.
    best_move = None
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            nd = cheb(nx, ny, rx, ry)
            # Prefer moves that keep/extend advantage versus opponent; slight bias toward target closeness.
            od = cheb(ox, oy, rx, ry)
            sd = nd
            adv = od - sd
            score = (-adv, nd, abs(nx - rx) + abs(ny - ry))
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]

    if best_move is None:
        # Fallback: deterministic safe step or stay.
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    return [dx, dy]
        return [0, 0]
    return best_move