def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "pursuer")).lower()
    evading = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 if d1 >= d2 else d2

    def obs_pen(nx, ny):
        pen = 0
        for bx, by in blocked:
            d = cheb(nx, ny, bx, by)
            if d == 0:
                return 10**9
            if d == 1:
                pen += 3
            elif d == 2:
                pen += 1
        return pen

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_corner = 0
        for cx, cy in corners:
            dc = cheb(nx, ny, cx, cy)
            if dc > d_corner:
                d_corner = dc

        # Pursuer: smaller distance to opponent, prefer moving toward a "tight" corner.
        # Evader: larger distance to opponent, prefer staying away from the pursuer while using far corners.
        # Obstacle proximity penalty deters trajectories that get stuck near obstacles.
        penalty = obs_pen(nx, ny)

        if evading:
            score = (d_opp * 10) + (d_corner * 2) - penalty
        else:
            score = (-d_opp * 10) + (-(max(cheb(nx, ny, cx, cy) for cx, cy in corners))) - (penalty * 2)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: prefer moves with larger dx then larger dy (consistent order).
            if dx > best_move[0] or (dx == best_move[0] and dy > best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]