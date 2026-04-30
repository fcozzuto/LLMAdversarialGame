def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # deterministic patrol towards center while keeping away from opponent
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = (md(nx, ny, tx, ty), -md(nx, ny, ox, oy), dx, dy)
            if best is None or val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose nearest resource (by Manhattan) as primary goal, then score moves.
    target = min(resources, key=lambda t: (md(sx, sy, t[0], t[1]), t[0], t[1]))
    tx, ty = target

    best_score = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_my = md(nx, ny, tx, ty)
        d_opp = md(ox, oy, tx, ty)

        # If we are at/near target, strongly favor finishing.
        # Also favor blocking: if opponent is closer, prefer moves that increase their advantage.
        # Add small deterministic tie-break by dx,dy.
        if d_my == 0:
            score = (-10**9, 0)
        else:
            score = (d_my,)

        # blocking/tempo term
        # prefer to reduce (d_opp - d_my) when opponent is currently closer
        gap_now = md(sx, sy, tx, ty) - md(ox, oy, tx, ty)
        gap_after = (d_my - d_opp)
        block_term = 0
        if gap_now > 0:
            block_term = gap_after  # smaller (more negative) is better: reduce opponent lead

        # keep away from opponent to reduce interference
        avoid_term = -md(nx, ny, ox, oy)

        # final lexicographic score
        val = (score[0], block_term, -avoid_term, dx, dy)
        if best_score is None or val < best_score:
            best_score = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]