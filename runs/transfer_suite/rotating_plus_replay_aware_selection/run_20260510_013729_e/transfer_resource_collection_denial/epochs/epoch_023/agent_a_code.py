def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacle_set = {(x, y) for x, y in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick best resource by arrival advantage, then closeness, then deterministic tiebreak.
    best = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prioritize states where we arrive sooner than opponent; break ties by our speed.
        key = (do - ds, -ds, -(rx * 8 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Move options: 8-neighbor + stay.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacle_set:
            continue

        ns = cheb(nx, ny, tx, ty)
        # Encourage improving distance to target, and slightly block opponent if they are closer to the same area.
        no = cheb(ox, oy, tx, ty)
        # If we reduce our distance meaningfully, prefer it.
        delta_self = (cheb(sx, sy, tx, ty) - ns)

        # Small penalty for moving away in x/y to avoid dithering.
        axis_pen = abs(nx - tx) + abs(ny - ty)

        # Deterministic tie-break prefers lexicographically smaller moves.
        score = (delta_self, -ns, -(abs(nx - ox) + abs(ny - oy)), -axis_pen, -((dx + 1) * 3 + (dy + 1)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]