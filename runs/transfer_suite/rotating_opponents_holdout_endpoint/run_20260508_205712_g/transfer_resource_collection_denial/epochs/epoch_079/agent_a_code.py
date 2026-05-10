def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    res = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res.append((int(p[0]), int(p[1])))

    def best_step(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(dx, dy), (dx, 0), (0, dy)]
        for cx, cy in candidates:
            nx, ny = sx + cx, sy + cy
            if inb(nx, ny):
                return [cx, cy]
        for cx, cy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + cx, sy + cy
            if inb(nx, ny):
                return [cx, cy]
        return [0, 0]

    if res:
        # pick deterministically: closest by manhattan; tie by lexicographic
        best = None
        for x, y in res:
            d = abs(x - sx) + abs(y - sy)
            score = (d, x, y)
            if best is None or score < best[0]:
                best = (score, x, y)
        _, tx, ty = best
        return best_step(tx, ty)

    # no resources: move away from opponent if possible, else toward a corner
    ax = -1 if ox > sx else (1 if ox < sx else 0)
    ay = -1 if oy > sy else (1 if oy < sy else 0)
    nx, ny = sx + ax, sy + ay
    if inb(nx, ny):
        return [ax, ay]

    corners = [(0, 0), (0, H - 1), (W - 1, 0), (W - 1, H - 1)]
    bestc = None
    for x, y in corners:
        d = abs(x - sx) + abs(y - sy)
        score = (d, x, y)
        if bestc is None or score < bestc[0]:
            bestc = (score, x, y)
    _, tx, ty = bestc
    return best_step(tx, ty)