def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Decide whether we should maximize distance (evader) or minimize (pursuer)
    we_evader = ("evader" in self_role) or ("pursuer" not in self_role and "evader" in opp_role)
    best = None
    best_key = None
    eps = 1 if cheb(sx, sy, ox, oy) > 0 else 0

    # Deterministic target bias: if evader, choose farthest corner; if pursuer, choose direction to reduce distance.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if we_evader:
        tcx, tcy = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -(c[0] + c[1]), c[0], c[1]) )
    else:
        tcx, tcy = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, tcx, tcy)
        # Tie-break uses coordinates for determinism
        if we_evader:
            key = (d_opp, d_corner, -(nx + ny), nx, ny)
        else:
            key = (-d_opp, -d_corner, (nx + ny), -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]