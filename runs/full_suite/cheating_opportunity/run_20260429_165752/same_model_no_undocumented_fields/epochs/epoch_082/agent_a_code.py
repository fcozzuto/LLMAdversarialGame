def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        bestv = None
        for rx, ry in resources:
            dm = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = dm - 0.35 * do
            # If opponent is extremely close, favor contesting that resource.
            if do <= 1: v -= 2.0
            if bestv is None or v < bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # If we can reach a resource immediately, prefer stepping onto it.
    step_res = None
    for dx, dy, nx, ny in cand:
        if (nx, ny) in set(resources):
            step_res = (dx, dy)
            break
    if step_res is not None:
        return [step_res[0], step_res[1]]

    opp_close = cheb(sx, sy, ox, oy) <= 2
    best_move = None
    best_score = None
    for dx, dy, nx, ny in cand:
        dm = cheb(nx, ny, tx, ty)
        dn = cheb(nx, ny, ox, oy)
        # Prefer reducing distance to target; avoid getting too close to opponent when already near.
        score = dm + (0.9 if not opp_close else 1.8) * (-dn)
        # Deterministic tie-breaker: prefer lexicographically smaller dx,dy after score.
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]