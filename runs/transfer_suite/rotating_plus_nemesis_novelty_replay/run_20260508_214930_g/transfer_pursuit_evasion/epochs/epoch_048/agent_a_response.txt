def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev

    # If we are on an obstacle (shouldn't happen), try to step out.
    if (sx, sy) in obs:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # 1-ply minimax: after our move, assume opponent moves to maximize our distance.
    best = None
    best_val = -10**9
    for mdx, mdy in deltas:
        nsx, nsy = sx + mdx, sy + mdy
        if not valid(nsx, nsy):
            continue
        # If capture possible immediately, take it.
        if nsx == ox and nsy == oy:
            return [mdx, mdy]

        worst = 10**9
        for edx, edy in deltas:
            nox, noy = ox + edx, oy + edy
            if not valid(nox, noy):
                nox, noy = ox, oy
            d = dist(nsx, nsy, nox, noy)
            if d < worst:
                worst = d

        # Prefer smaller worst-case distance; tie-break toward reducing Manhattan and corner pressure.
        # (Corner pressure helps against zigzags that try to run.)
        corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
        corner = min(corners, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))
        corner_dx = abs(corner[0] - nsx) + abs(corner[1] - nsy)
        mman = abs(nsx - ox) + abs(nsy - oy)
        key = (-worst, -mman, -corner_dx)
        if best is None or key > best_val:
            best_val = key
            best = (mdx, mdy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]