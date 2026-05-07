def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources and (sx, sy) in set(tuple(r) for r in resources) and (sx, sy) not in obstacles:
        return [0, 0]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        cx, cy = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), -abs(c[0] - sx) - abs(c[1] - sy)))
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not inb(sx + dx, sy + dy):
            best = max(legal, key=lambda m: abs((sx + m[0]) - ox) + abs((sy + m[1]) - oy))
            return [best[0], best[1]]
        return [dx, dy]

    res = [tuple(r) for r in resources]

    def eval_pos(px, py):
        best = None
        for rx, ry in res:
            d_self = abs(rx - px) + abs(ry - py)
            d_opp = abs(rx - ox) + abs(ry - oy)
            adv = (d_opp - d_self)  # higher means we arrive first
            val = (adv, -d_self, -abs((rx - px) - (ry - py)))  # tie-break deterministic
            if best is None or val > best[0]:
                best = (val, (rx, ry), d_self, d_opp)
        return best[0]

    best_move = None
    best_val = None
    for dx, dy in legal:
        px, py = sx + dx, sy + dy
        val = eval_pos(px, py)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]