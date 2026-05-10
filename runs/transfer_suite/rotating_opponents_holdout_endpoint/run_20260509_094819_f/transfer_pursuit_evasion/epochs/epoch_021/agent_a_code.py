def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def exits(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    ti = int(observation.get("turn_index", 0) or 0)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corners2 = [(w - 1, w - 1) if w == h else (w - 1, h - 1), (0, h - 1), (w - 1, 0), (0, 0)]
    tx, ty = corners[ti % 4]
    if not is_evader:
        tx, ty = ox, oy

    # If in evader role, sometimes bias toward far corner; otherwise, sometimes bias toward blocking lines.
    if is_evader:
        if (ti % 4) == 1:
            tx, ty = corners2[ti % 4]
        if (tx, ty) in blocked:
            tx, ty = corners[2 if (ti % 4) == 1 else 3]

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_tar = cheb(nx, ny, tx, ty)
        e = exits(nx, ny)

        if is_evader:
            # Maximize distance from pursuer; tie-break by distance to target; then by having more exits.
            val = (d_opp, d_tar, e, -abs((nx - sx) + (ny - sy)))
        else:
            # Minimize distance from evader (opponent); tie-break by closeness to target if set; then by exits.
            val = (-d_opp, -d_tar, e, -abs((nx - sx) + (ny - sy)))

        if best is None:
            best = (dx, dy)
            best_val = val
        else:
            if val > best_val:
                best = (dx, dy)
                best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]