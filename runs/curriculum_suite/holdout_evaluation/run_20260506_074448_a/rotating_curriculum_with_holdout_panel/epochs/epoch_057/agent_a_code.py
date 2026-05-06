def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    best_key = None
    best_move = [0, 0]

    if not resources:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        my_to_opp = man(nx, ny, ox, oy)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Race advantage: favor states that reduce our distance vs opponent for the same resource.
            score += (opd - myd)
            # Small regularization: prefer resources closer to us now.
            score -= 0.08 * myd
        # Counter "edge patrol": prefer interior cells (harder for edge-focused opponent to contest).
        score += 0.20 * edge_dist(nx, ny)
        # Mild safety: avoid moving too far from opponent when advantage is similar (reduces being outflanked).
        score -= 0.01 * my_to_opp

        key = (-score, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_key is not None else [0, 0]