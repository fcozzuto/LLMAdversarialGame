def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def king(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) >= abs(dy) else abs(dy)

    # Choose target by "can we arrive first?" then by how soon and how central it is.
    cx = (w - 1) * 0.5
    cy = (h - 1) * 0.5
    best = None
    for rx, ry in res:
        ds = king(sx, sy, rx, ry)
        do = king(ox, oy, rx, ry)
        margin = do - ds  # positive => we're earlier
        center = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        # If we're not confident to beat opponent, still prefer resources slightly ahead of them (denial pressure).
        if margin >= 0:
            score = 10_000 + 2_000 * margin + (-ds) + 0.01 * center
        else:
            score = 1_000 + 400 * (margin) + (-ds) + 0.02 * center
        if best is None or score > best[0] or (score == best[0] and ds < best[2]):
            best = (score, (rx, ry), ds)

    tx, ty = best[1]

    # If opponent is essentially as close or closer to our chosen target, steer slightly to a safer intermediate
    # (resource deniers often lurk; this reduces direct head-to-head).
    if king(ox, oy, tx, ty) - king(sx, sy, tx, ty) >= 1:
        # Try an intermediate near the midpoint between us and target, with a slight bias away from opponent.
        mx = (sx + tx) // 2
        my = (sy + ty) // 2
        if abs(ox - mx) <= abs(tx - ox):
            mx = (mx + (mx - ox)) // 2
        if abs(oy - my) <= abs(ty - oy):
            my = (my + (my - oy)) // 2
        if 0 <= mx < w and 0 <= my < h and (mx, my) not in obstacles:
            tx, ty = mx, my

    # Move one step toward (tx, ty), with obstacle-aware fallback among 8-neighborhood moves.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Prefer moves that reduce distance to target; break ties by reducing opponent distance; then centrality.
    bestm = None
    for dx, dy, nx, ny in candidates:
        d_to_t = king(nx, ny, tx, ty)
        d_opp = king(nx, ny, ox, oy)
        central = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # If we can collect immediately, prioritize it strongly.
        collect_now = 1 if (nx, ny) in set(res) else 0
        score = 1_000_000 * collect_now - 10_000 * d_to_t - 50 * d_opp + 0.01 * central
        if bestm is None or score > bestm[0]:
            bestm = (score, dx, dy)

    return [int(bestm[1]), int(bestm[2])]