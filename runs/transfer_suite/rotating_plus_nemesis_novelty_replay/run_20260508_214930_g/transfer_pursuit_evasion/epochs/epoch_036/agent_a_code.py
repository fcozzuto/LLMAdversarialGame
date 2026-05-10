def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Evader tendency: head to corner farthest from our current position
    corner = None
    bestc = None
    for cx, cy in corners:
        d = abs(cx - sx) + abs(cy - sy)
        if bestc is None or d > bestc:
            bestc = d
            corner = (cx, cy)
    tx, ty = corner

    # Predict opponent next step under obstacle-aware greedy move toward that corner
    expected = (ox, oy)
    bestop = None
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if bestop is None or d < bestop or (d == bestop and (dx, dy) < (expected[0] - ox, expected[1] - oy)):
            bestop = d
            expected = (nx, ny)

    ex, ey = expected

    # Chase the predicted position (pursuer objective)
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        d = (nx - ex) * (nx - ex) + (ny - ey) * (ny - ey)
        # Small bias: also reduce Chebyshev distance to actual opponent if tie
        cheb = max(abs(nx - ox), abs(ny - oy))
        key = (d, cheb, dx, dy)
        if best is None or key < best:
            best = key
    if best is None:
        return [0, 0]
    return [best[2], best[3]]