def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        ax = abs(x - ox); ay = abs(y - oy)
        return ax if ax > ay else ay

    # If evading, bias toward the corner farthest from opponent; if pursuing, bias toward that corner only when it shortens distance.
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    far_corner = None
    best_fc = -1
    for cx, cy in corners:
        d = abs(cx - ox) + abs(cy - oy)
        if d > best_fc:
            best_fc = d
            far_corner = (cx, cy)
    fc_x, fc_y = far_corner

    best = None  # (score, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = cheb(nx, ny)
        wall_margin = min(nx, ny, w - 1 - nx, h - 1 - ny)
        # Deterministic tie-breaker: prefer moves with consistent ordering via score then (dx,dy).
        if is_evader:
            # Primary: maximize distance. Secondary: move toward far corner. Tertiary: avoid tight walls (stay a bit open).
            corner_improve = -(abs(nx - fc_x) + abs(ny - fc_y))
            score = (dist * 1000) + (corner_improve * 3) + (wall_margin * 2)
        else:
            # Pursuer: minimize distance; then move toward opponent's vicinity by reducing Manhattan; avoid being pinned near walls.
            corner_reduce = (-(abs(nx - ox) + abs(ny - oy)))
            score = (-dist * 1000) + (corner_reduce * 2) + (wall_margin)
        cand = (score, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]