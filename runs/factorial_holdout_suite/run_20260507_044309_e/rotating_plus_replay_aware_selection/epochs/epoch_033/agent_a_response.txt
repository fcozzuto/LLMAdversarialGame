def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def best_value(x, y):
        if not resources:
            tx, ty = w // 2, h // 2
            return -cheb(x, y, tx, ty), 0, (tx, ty)
        bestv = -10**18
        bestt = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # we arrive earlier => positive
            center = cheb(rx, ry, w // 2, h // 2)
            v = lead * 1000 - ds * 6 - center
            if v > bestv:
                bestv = v
                bestt = (rx, ry)
        return bestv, 0, bestt

    # Evaluate moves by resulting position; deterministic tie-break by delta order
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        v, _, _ = best_value(nx, ny)
        # small preference to keep moving toward center when equal
        center_pref = -cheb(nx, ny, w // 2, h // 2) * 0.01
        score = v + center_pref
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves invalid, stay
    return best_move if isinstance(best_move, list) else [0, 0]