def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("evader" in opp_role) and ("pursuer" not in self_role))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Obstacle proximity (prefer moves that increase clearance)
    def obs_clear(x, y):
        best = 10**9
        for (bx, by) in obstacles:
            d = cheb(x, y, bx, by)
            if d < best:
                best = d
        return best if obstacles else 99

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        clr = obs_clear(nx, ny)
        # Mild anti-corner trapping for evader, mild central drift for pursuer
        centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
        cen = abs(nx - centerx) + abs(ny - centery)

        if is_evader:
            score = (d * 100.0) + (clr * 2.0) - (cen * 0.02)
            # Try to avoid giving immediate capture
            if d == 0:
                score -= 1e6
        else:
            score = (-d * 100.0) + (clr * 1.5) - (cen * 0.01)
            if d == 0:
                score += 1e6  # immediate capture
        moves.append((score, dx, dy, nx, ny, d, clr))

    if not moves:
        return [0, 0]

    # Deterministic tie-break: higher score, then dx, then dy, then smaller distance if tie
    moves.sort(key=lambda t: (t[0], -t[3], -t[4], -t[5], -t[6], -t[1], -t[2]), reverse=True)
    return [int(moves[0][1]), int(moves[0][2])]