def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    if not resources:
        # Move to corner farthest from opponent, prefer progressing outward.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None; bestv = None
        for cx, cy in corners:
            d_opp = abs(cx - ox) + abs(cy - oy)
            d_self = abs(cx - sx) + abs(cy - sy)
            v = (d_opp, -d_self, cx, cy)
            if bestv is None or v > bestv:
                bestv = v; best = (cx, cy)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles:
            return [dx, dy]
        return [0, 0]

    # Heuristic: after one move, choose a target resource closest to us, but
    # score by how much farther it is from opponent (resource-denial).
    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        best_res = None; best_key = None
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we reach quickly; among those, prefer ones opponent is far from.
            key = (-ds, do, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)
        rx, ry = best_res
        ds = abs(rx - nx) + abs(ry - ny)
        do = abs(rx - ox) + abs(ry - oy)
        # Also encourage reducing relative distance advantage.
        rel = (do - ds)
        # Tie-break deterministically by closer to opponent? prefer not.
        return (rel, -ds, -abs(nx - ox) - abs(ny - oy), dx, dy)

    best_move = None; bestv = None
    for dx, dy in legal:
        v = eval_move(dx, dy)
        if bestv is None or v > bestv:
            bestv = v; best_move = (dx, dy)

    return [best_move[0], best_move[1]]