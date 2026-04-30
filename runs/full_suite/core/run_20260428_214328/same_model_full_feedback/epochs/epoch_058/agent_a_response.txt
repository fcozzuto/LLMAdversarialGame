def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy  # squared distance

    if not deltas:
        return [0, 0]

    # If there are no resources visible, block by getting closer to opponent while staying safe.
    if not resources:
        best = None
        best_m = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            m = cheb(nx, ny, ox, oy)
            # deterministic tie-break: prefer smaller dx, then smaller dy
            key = (m, dx, dy)
            if best is None or key < best:
                best = key
                best_m = (dx, dy)
        return list(best_m if best_m is not None else (0, 0))

    # Score moves by contesting the closest "valuable" resource to either us or opponent.
    best_key = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Choose a target resource deterministically: minimize min(my,opp) distance (squared).
        best_target = None
        best_td = None
        for rx, ry in resources:
            dmi = cheb(nx, ny, rx, ry)
            doi = cheb(ox, oy, rx, ry)
            t = dmi if dmi < doi else doi  # whichever side is closer
            key = (t, rx, ry)
            if best_target is None or key < best_td:
                best_target = (rx, ry)
                best_td = key

        rx, ry = best_target
        d_my = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        d_opp_next = min(cheb(ox + adx, oy + ady, rx, ry) for adx, ady in deltas if inside(ox + adx, oy + ady)) if any(inside(ox + adx, oy + ady) for adx, ady in deltas) else d_opp

        # Prefer: be closer than opponent to the contested target; otherwise deny by reducing their advantage.
        # Also slightly penalize moving farther from self-opponent center to avoid dead-ends.
        score = (d_my - d_opp) + 0.15 * (d_my - d_opp_next)

        # Deterministic tie-break: prefer lower score, then closer to opponent (smaller dist), then dx/dy ordering.
        key = (score, cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]