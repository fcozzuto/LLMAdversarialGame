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

    # Prefer resources where opponent is farther (max margin), then closer by our Chebyshev distance.
    best = None
    best_key = (-10**9, 10**9)
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        key = (margin, sd)
        if key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # One-step lookahead: pick move that maximizes future advantage vs nearest resource to us.
    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best_mv = (0, 0)
    best_sc = (-10**18, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # Our nearest distance; opponent nearest distance (fixed position).
        my_d = 10**9
        opp_d = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            if d1 < my_d: my_d = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < opp_d: opp_d = d2
        sc = (opp_d - my_d, -my_d)  # primary: more advantage; secondary: closer
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]