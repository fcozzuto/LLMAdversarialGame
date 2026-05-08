def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manhattan(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # One-step greedy with obstacle-aware tie-breaking
    best = [0, 0]
    if not self_is_evader:
        # Pursuer: minimize distance; if blocked, avoid becoming cornered by preferring max clearance.
        def score(nx, ny):
            d = manhattan(nx, ny, ox, oy)
            # clearance: number of free neighboring cells
            c = 0
            for dx, dy in moves:
                tx, ty = nx + dx, ny + dy
                if free(tx, ty):
                    c += 1
            return (d, -c, nx, ny)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            k = score(nx, ny)
            if best_key is None or k < best_key:
                best_key = k
                best = [dx, dy]
        return best

    # Evader: maximize distance; bias toward moves that reduce pursuer's options (indirectly).
    # Deterministic "escape vector": head to the farthest corner if reachable, else follow local maximize.
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    far_corner = max(corners, key=lambda c: (manhattan(c[0], c[1], ox, oy), -c[0], -c[1]))

    def score(nx, ny):
        d = manhattan(nx, ny, ox, oy)
        # also move toward far_corner (only as tie-breaker)
        dc = manhattan(nx, ny, far_corner[0], far_corner[1])
        # and reduce pursuer's mobility from its next position guess (conservative)
        # We approximate by counting how many free cells around current opponent exist.
        opp_mob = 0
        for ddx, ddy in moves:
            tx, ty = ox + ddx, oy + ddy
            if free(tx, ty):
                opp_mob += 1
        return (-d, dc, -opp_mob, nx, ny)

    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        k = score(nx, ny)
        if best_key is None or k < best_key:
            best_key = k
            best = [dx, dy]
    return best