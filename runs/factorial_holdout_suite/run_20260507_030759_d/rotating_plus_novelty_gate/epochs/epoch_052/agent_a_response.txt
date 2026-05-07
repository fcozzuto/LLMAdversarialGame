def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = set(tuple(p) for p in (observation.get("resources", []) or []))

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if (sx, sy) in resources:
        return [0, 0]
    if not resources:
        # fallback: increase distance from opponent while moving to any open neighbor
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = (manh(nx, ny, sx, sy) * 0 - manh(nx, ny, ox, oy), dx, dy)
            if best is None or val < best:
                best = val
        return [best[1], best[2]]

    # For each move, pick the most favorable resource (self-first with opponent lead), then score the move.
    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # choose target resource deterministically
        best_res = None
        best_key = None
        for rx, ry in resources:
            ds = manh(nx, ny, rx, ry)
            do = manh(nx, ny, ox, oy)
            # prefer smaller self distance, but also where we keep/extend the lead
            key = (ds - (do - ds) * 0.35, ds, -do, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_res = (rx, ry)
        rx, ry = best_res
        self_d = manh(nx, ny, rx, ry)
        opp_d = manh(nx, ny, ox, oy)
        # move value: maximize our lead at the target, then minimize our distance, then prefer progress toward opponent's position
        val = ((opp_d - self_d), -(self_d), -(manh(nx, ny, ox, oy)), -dx, -dy)
        if best_move is None or val > best_move[0]:
            best_move = (val, dx, dy)

    return [best_move[1], best_move[2]]