def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    moves.sort()  # deterministic tie-break

    if not resources:
        # Deterministic drift to own side center
        tx, ty = (w // 4) - 0, (h // 2)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Deny-focused: maximize our safety margin against the opponent's best grab.
        # For each resource, margin = (opp_dist - self_dist). Higher means we arrive earlier.
        worst_margin = 10**18
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            margin = opp_d - self_d
            if margin < worst_margin:
                worst_margin = margin
        # Secondary: prefer smaller distance to the best (most dangerous) resource
        # where opponent is relatively closer.
        danger = 10**18
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            rel = self_d - opp_d  # smaller => we are later
            if rel < danger:
                danger = rel
        val = (worst_margin, -danger, -abs(nx - sx) - abs(ny - sy), -dx, -dy)
        if val > (best_val, 0, 0, 0, 0):
            best_val = val[0]
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]