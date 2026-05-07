def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and ok(x, y):
                ds = cheb(sx, sy, x, y)
                do = cheb(ox, oy, x, y)
                valid_res.append((x, y, ds, do))
    if not valid_res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that improve "can reach first" and reduce distance.
    best = (None, -10**9)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        score = 0
        # Evaluate against nearest few resources (deterministic, bounded work)
        # Sort by our distance, then resource coords for determinism.
        candidates = sorted(valid_res, key=lambda t: (t[2], t[0], t[1]))
        count = 0
        for x, y, ds, do in candidates:
            # recompute ds for moved position
            nds = cheb(nx, ny, x, y)
            gap = do - nds
            # gap > 0 means we can arrive strictly sooner (or tie with bonus)
            if gap > 0:
                score += 2000 + gap * 40 - nds
            elif gap == 0:
                score += 700 - nds
            else:
                score += - (nds - do) * 60 - nds * 2
            # Small bias to avoid wasting steps once close
            if nds <= 1:
                score += 120
            count += 1
            if count >= 4:
                break
        # If we can capture a resource immediately, strongly prefer it
        if any(nx == x and ny == y for x, y, _, _ in valid_res):
            score += 50000
        if score > best[1]:
            best = ((dxm, dym), score)
    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]