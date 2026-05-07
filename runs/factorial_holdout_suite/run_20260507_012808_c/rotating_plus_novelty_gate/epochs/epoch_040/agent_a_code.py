def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick best resource by: (opponent advantage over us) then closeness.
    best_rx, best_ry = resources[0]
    best_margin = -10**9
    best_dist = 10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # higher means opponent is farther relative to us
        if margin > best_margin or (margin == best_margin and (ds < best_dist)):
            best_margin = margin
            best_dist = ds
            best_rx, best_ry = rx, ry

    # Local greedy step toward target, with one-ply obstacle check and tie-breaks.
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, best_rx, best_ry)
        # also softly prefer reducing opponent distance to the same target
        do = cheb(ox, oy, best_rx, best_ry)
        # deterministic tie-break: smallest ds, then smallest (nx+ny), then dx,dy
        candidates.append((ds, nx + ny, dx, dy, do))
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(candidates[0][2]), int(candidates[0][3])]