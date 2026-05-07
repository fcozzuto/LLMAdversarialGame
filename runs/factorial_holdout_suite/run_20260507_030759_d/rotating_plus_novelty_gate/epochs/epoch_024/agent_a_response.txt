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
    if not resources:
        # deterministically move toward opponent corner-ish (resource-less fallback)
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx if dx in (-1, 0, 1) else 0, dy if dy in (-1, 0, 1) else 0]

    # Opponent is a "denier": prioritize actions that maximize our distance advantage
    # on the same resource, else minimize how badly we lag behind.
    def best_resource_gap(px, py):
        best = None  # (gap, -d_me, tb)
        for rx, ry in resources:
            d_me = abs(rx - px) + abs(ry - py)
            d_op = abs(rx - ox) + abs(ry - oy)
            gap = d_op - d_me
            tb = -(rx * 8 + ry)
            cand = (gap, -d_me, tb)
            if best is None or cand > best:
                best = cand
        return best  # (gap, -d_me, tb)

    best_move = None  # (score, dx, dy)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        gap, neg_d_me, _tb = best_resource_gap(nx, ny)
        # Prefer larger gap (we arrive first), then closer to that resource.
        score = gap * 1000 + neg_d_me * 10
        if best_move is None or (score, dx, dy) > best_move:
            best_move = (score, dx, dy)
    return [best_move[1], best_move[2]]