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

    # Intercept sweep_rows: if we can contest resources on opponent's current row, prioritize them.
    row_resources = [(x, y) for (x, y) in resources if y == oy]
    if row_resources:
        tx, ty = min(row_resources, key=lambda c: (md(sx, sy, c[0], c[1]), c[0], c[1]))
    else:
        best = None
        for x, y in resources:
            my = md(sx, sy, x, y)
            opp = md(ox, oy, x, y)
            # Prefer targets where we are closer than the opponent; otherwise minimize how badly we're behind.
            adv = opp - my
            key = (-(adv), my, x, y)  # smallest is best
            if best is None or key < best[0]:
                best = (key, (x, y))
        tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((md(nx, ny, tx, ty), abs(dx) + abs(dy), dx, dy))
    if not candidates:
        return [0, 0]
    _, _, dx, dy = min(candidates, key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(dx), int(dy)]