def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    selfT = set(tuple(t) for t in (observation.get("self_territory") or []))
    oppT = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def neigh4(x, y):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                yield nx, ny

    # Determine a deterministic target preference.
    best_target = None
    best_td = 10**9
    for (x, y) in unclaimed:
        if (x, y) in blocked:
            continue
        d = abs(x - sx) + abs(y - sy)
        # Prefer cells adjacent to our territory.
        adj = 0
        for nx, ny in neigh4(x, y):
            if (nx, ny) in selfT:
                adj = 1
                break
        score_key = (0 if adj else 1, d, abs(x - cx) + abs(y - cy), y, x)
        if score_key < best_td:
            best_td = score_key
            best_target = (x, y)

    if best_target is None:
        # Fallback: go toward center, but avoid blocked.
        best_target = (int(round(cx)), int(round(cy)))

    tx, ty = best_target

    # One-step evaluation.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0
        val = 0
        t = (nx, ny)
        if t in unclaimed:
            val += 600
        if t in oppT:
            # Flip can help, but still prefer unclaimed/frontier.
            val += 120 - (abs(nx - tx) + abs(ny - ty))
        if t in selfT:
            val += 30
        # Frontier pull: prefer unclaimed adjacent to our current territory.
        for ax, ay in neigh4(nx, ny):
            if (ax, ay) in unclaimed and (ax, ay) not in blocked:
                val += 80
                break
        # Aim toward target.
        val += - (abs(nx - tx) + abs(ny - ty))
        # Mild safety: stay away from obstacles by rewarding fewer adjacent blocked cells.
        adj_blocked = 0
        for ax, ay in neigh4(nx, ny):
            if (ax, ay) in blocked:
                adj_blocked += 1
        val += -20 * adj_blocked
        # Deterministic tie-break: prefer earlier dirs order implicitly.
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move