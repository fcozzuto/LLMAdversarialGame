def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0), int(op[1] or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Prioritize contesting resources on opponent's current row; else race for best "advantage".
    row_targets = [c for c in resources if c[1] == oy]
    if row_targets:
        tx, ty = min(row_targets, key=lambda c: (md(sx, sy, c[0], c[1]), c[0], c[1]))
    else:
        best = None
        for x, y in resources:
            my = md(sx, sy, x, y)
            oo = md(ox, oy, x, y)
            # Favor targets we're closer to; slight tie-break by lower x/y for determinism.
            score = (my - oo * 0.85, my, x, y)
            if best is None or score < best[0]:
                best = (score, x, y)
        tx, ty = best[1], best[2]

    # Choose a valid step that reduces distance to target; block obstacles; deterministic tie-break.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = md(nx, ny, tx, ty)
        o_nextd = md(ox, oy, tx, ty)
        # Slight preference to keep opponent from reducing their own distance too much.
        s = (myd, md(ox, oy, nx, ny), -(o_nextd), dx, dy)
        if bestm is None or s < bestm[0]:
            bestm = (s, dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]