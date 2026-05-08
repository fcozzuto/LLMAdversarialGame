def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return inside(x, y) and (x, y) not in blocked

    # Target bias for evasion: go to farther corner; for pursuit: chase opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        # If already close to that corner, drift to opposite corner to avoid wall-traps.
        if cheb(sx, sy, tx, ty) <= 2:
            tx, ty = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    best_move = [0, 0]
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, tx, ty)

        # Obstacle-aware: prefer moves with more available neighbor squares.
        avail = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if free(ax, ay):
                avail += 1

        # Pursuer tries to reduce distance to opponent quickly.
        # Evader tries to increase distance while reducing distance to chosen corner.
        if is_evader:
            # Strongly maximize separation; secondary drive to corner; avoid being boxed in.
            val = d_opp * 1000 - d_corner * 3 + avail
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            # Strongly minimize separation; secondary keep moving toward "target" and away from corners if it helps avoid stalling.
            # Also prefer positions with better mobility.
            val = d_opp * -1000 + d_corner * -1 + avail * 2
            # val is larger is better; convert to minimization by negating to keep structure consistent
            if val > -best_val:
                best_val = -val
                best_move = [dx, dy]

    return best_move