def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    res_set = set(resources)
    if (sx, sy) in res_set:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer taking a resource that increases our distance advantage and is "less shared"
        # (quadratic bias away from opponent relative position).
        bias = (rx - ox) * (sx - ox) + (ry - oy) * (sy - oy)
        key = (od - sd, -bias, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            nsd = cheb(nx, ny, tx, ty)
            nod = cheb(ox, oy, tx, ty)  # opponent assumed static this turn
            # Prefer immediate gain, then decreasing distance, then closer to any resource pickup.
            # Include deterministic tiebreaker by coordinates.
            closest_res = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources) if resources else 0
            gain = (nod - nsd) - (cheb(sx, sy, tx, ty) * 0)  # keeps sign consistent
            key = (gain, -nsd, -closest_res, nx, ny, dx, dy)
            moves.append((key, [dx, dy]))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0], reverse=True)
    return moves[0][1]