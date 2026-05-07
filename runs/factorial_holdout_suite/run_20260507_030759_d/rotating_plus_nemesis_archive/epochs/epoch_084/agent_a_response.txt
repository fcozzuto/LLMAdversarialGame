def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    if not resources:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we are most ahead vs opponent; tie by smaller self distance then deterministic coord.
    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = od - sd
        key = (lead, -sd, -tx, -ty)  # deterministic; prefers larger lead, then shorter distance, then stable ordering
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # Move one step toward target (8-way including stay), avoiding obstacles if possible.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    bestm = [0, 0]
    bestm_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target; Secondary: keep our advantage vs opponent; Tertiary: deterministic ordering.
        nd = cheb(nx, ny, tx, ty)
        my_next = cheb(nx, ny, tx, ty)
        opp_next = cheb(ox, oy, tx, ty)
        lead_next = opp_next - my_next
        key = (-nd, lead_next, dx, dy)
        if bestm_key is None or key > bestm_key:
            bestm_key = key
            bestm = [dx, dy]

    if bestm_key is None:
        return [0, 0]
    return bestm