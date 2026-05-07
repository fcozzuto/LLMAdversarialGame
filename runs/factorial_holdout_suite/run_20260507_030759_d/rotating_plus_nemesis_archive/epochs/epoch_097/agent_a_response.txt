def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources or (sx, sy) in obstacles:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we are closer than opponent; otherwise block by minimizing opponent lead.
    best = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = od - sd  # positive means opponent farther
        # Primary: maximize lead; Secondary: smaller self distance; Tertiary: deterministic tie-break
        key = (lead, -sd, -tx, -ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty), sd, od)
    (tx, ty) = best[1]

    # Choose a move among 8-neighborhood + stay, avoiding obstacles when possible.
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)
        # Prefer reducing distance to target; if tied, keep away from opponent; then deterministic tie-break.
        key = (-nd, nod, dx, dy)
        candidates.append((key, (dx, dy)))
    if candidates:
        candidates.sort(reverse=True, key=lambda z: z[0])
        return [int(candidates[0][1][0]), int(candidates[0][1][1])]

    # If all safe moves blocked, allow staying.
    return [0, 0]