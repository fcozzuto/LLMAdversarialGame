def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    target = None
    if res:
        best = None
        bestk = None
        for rx, ry in res:
            dme = cheb(sx, sy, rx, ry)
            dob = cheb(ox, oy, rx, ry)
            k = (dme - dob, dme, rx, ry)  # prefer resources where we're relatively closer
            if best is None or k < bestk:
                best = (rx, ry)
                bestk = k
        target = best

    if target is None:
        # deterministic fallback: head toward center
        tx, ty = (W - 1) // 2, (H - 1) // 2
    else:
        tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obs:
            continue
        d = cheb(nx, ny, tx, ty)
        dob_after = cheb(ox + 0, oy + 0, tx, ty)  # opponent position unchanged this turn
        # Prefer getting closer; slightly prefer states where opponent is relatively farther
        score = (d, -((dob_after - d) if dob_after != d else 0), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]