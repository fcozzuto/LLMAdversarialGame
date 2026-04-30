def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand.sort()

    # If no resources, move to center-ish while avoiding obstacles.
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        bestv = -10**18
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            score = -d
            if score > bestv:
                bestv = score
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Pick the move that most improves our relative closeness to some resource.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Evaluate best target from our perspective after this move.
        local_best = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            ds2 = cheb(nx, ny, rx, ry)

            # Want ds2 < do, while also reducing do - ds and pushing for nearer targets.
            gap_before = ds - do
            gap_after = ds2 - do
            delta_gap = gap_before - gap_after  # positive means we improved our standing

            # Prefer resources where opponent is relatively far, and avoid walking far off.
            far_for_opp = do
            proximity = ds2

            score = delta_gap * 120 - gap_after * 60 + far_for_opp * 2 - proximity
            if score > local_best:
                local_best = score

        # Tiebreak deterministically: prefer staying closer to improving.
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]