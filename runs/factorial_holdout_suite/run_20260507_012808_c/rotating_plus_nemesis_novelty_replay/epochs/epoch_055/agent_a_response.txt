def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):  # |a-c|+|b-d|
        ad = a - c
        bd = b - d
        if ad < 0: ad = -ad
        if bd < 0: bd = -bd
        return ad + bd

    if not resources:
        # Move toward the corner that is farthest from opponent (reduce being blocked)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        ti = int(observation.get("turn_index", 0) or 0)
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            val = (man(ox, oy, cx, cy) - man(sx, sy, cx, cy), (cx + cy + ti) % 7)
            if best is None or val > best[0]:
                best = (val, cx, cy)
        if best is None:
            return [0, 0]
        tx, ty = best[1], best[2]
    else:
        ti = int(observation.get("turn_index", 0) or 0)
        # Pick resource where we arrive sufficiently earlier than opponent, but also keep progress.
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # higher is better
            # Prefer: we faster (do - ds), then lower ds.
            val = (do - ds, -ds, (rx * 3 + ry * 5 + ti) % 11)
            if best is None or val > best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]

    # Choose a safe step that reduces distance to target; deterministic tie-break via small preference order.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index", 0) or 0)
    bestm = None
    bestkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Primary: minimize distance to target; Secondary: maximize distance difference to opponent.
        ns = man(nx, ny, tx, ty)
        no = man(nx, ny, ox, oy)
        key = (ns, -no, (dx + 2 * dy + ti) % 7)
        if bestkey is None or key < bestkey:
            bestkey = key
            bestm = (dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]