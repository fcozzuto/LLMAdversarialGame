def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("evade" in role) or ("runner" in role) or ("escape" in role)

    # Heuristic target: evader runs to farthest corner; pursuer goes straight toward opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: dist(c[0], c[1], ox, oy))
        # Score: maximize distance to opponent; bias toward target corner; avoid low-mobility squares.
        def score(nx, ny):
            if not valid(nx, ny):
                return -10**9
            d_opp = dist(nx, ny, ox, oy)
            d_tar = dist(nx, ny, tx, ty)
            mob = 0
            for ddx, ddy in moves:
                nnx, nny = nx + ddx, ny + ddy
                if valid(nnx, nny):
                    mob += 1
            return (d_opp * 100) - d_tar * 3 + mob
    else:
        # Pursuer: minimize distance to opponent; prefer not trapping behind obstacles.
        def score(nx, ny):
            if not valid(nx, ny):
                return -10**9
            d_opp = dist(nx, ny, ox, oy)
            mob = 0
            for ddx, ddy in moves:
                nnx, nny = nx + ddx, ny + ddy
                if valid(nnx, nny):
                    mob += 1
            return (-d_opp * 100) + mob

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: prefer moves with smallest dx, then dy, in that order, but only after score.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]