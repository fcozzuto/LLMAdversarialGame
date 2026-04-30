def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    occ = {(p[0], p[1]) for p in obstacles}
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def danger(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in occ:
                    pen += 3 if (dx == 0 or dy == 0) else 2
        return pen

    # Choose the resource that gives the biggest advantage, then pick the move that improves it.
    best_r = None
    best_r_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Advantage for us; also slightly avoid being too close to opponent already.
        key = (do - ds, -ds, rx, ry)
        if best_r_key is None or key > best_r_key:
            best_r_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = [0, 0]
    best_score = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds) * 120 - ds * 8 - danger(nx, ny) * 15
        # Small bias: move toward center-ish to reduce corner trapping.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= (abs(nx - cx) + abs(ny - cy)) * 0.5
        if score > best_score:
            best_score = score
            best_move = [dxm, dym]

    return best_move