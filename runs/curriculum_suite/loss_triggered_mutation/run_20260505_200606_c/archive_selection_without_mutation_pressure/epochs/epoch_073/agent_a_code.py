def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def clamp_cell(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev for movement speed on diagonals
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_cell(nx, ny) or (nx, ny) in obstacles:
            continue

        best_here = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_our = dist((nx, ny), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))

            # Prefer resources we can beat soon; otherwise, maximize opponent delay.
            # Add slight center preference to avoid getting funneled along edges.
            center_pen = abs(nx - cx) + abs(ny - cy)
            # Threat term: larger means opponent advantage; we want smaller/negative.
            threat = (d_opp - d_our)

            score = (-(d_our) * 2.0) + (threat * 1.5)
            score += (-0.08 * center_pen)

            # If our path is already as good or better, amplify.
            if d_our <= d_opp:
                score += 6.0 + (d_opp - d_our) * 0.5

            if score > best_here:
                best_here = score

        # Tie-break deterministically: prefer staying closer to center and then minimal dx/dy sum.
        tie_key = (-(best_here), abs(nx - cx) + abs(ny - cy), abs(dx) + abs(dy), dx, dy)
        if best is None or tie_key < best[0]:
            best = (tie_key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]