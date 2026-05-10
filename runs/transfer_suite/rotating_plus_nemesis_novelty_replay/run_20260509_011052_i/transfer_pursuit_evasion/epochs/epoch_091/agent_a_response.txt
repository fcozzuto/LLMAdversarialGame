def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    role = (observation.get("self_role") or "").lower()
    pursue = (role != "evader")

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Opponent tends to a corner: predict nearest corner to opponent.
    target_corner = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
    tx, ty = target_corner

    best = None
    best_score = -10**30 if pursue else 10**30
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        step = 0 if (dx == 0 and dy == 0) else 1

        # Pursuer: close distance; also get in front of the opponent's likely corner.
        # Evader: maximize distance; also head toward the farthest corner.
        if pursue:
            # "Cutoff" pressure: prefer positions that reduce opponent's progress to its corner
            # while decreasing the immediate distance.
            to_corner = cheb(nx, ny, tx, ty)
            opp_to_corner = cheb(ox, oy, tx, ty)
            # If we are already nearer to that corner than opponent is, it's a strong block.
            block = 1 if cheb(nx, ny, tx, ty) <= opp_to_corner else 0
            score = (-d * 100000) + (-to_corner * 50) + (block * 5000) + (step * 5)
            # Tiny deterministic tie-break: prefer moves toward decreasing both axes distance to opponent.
            score += -abs(nx - ox) - abs(ny - oy) * 0.001
            if score > best_score:
                best_score = score
                best = [dx, dy]
        else:
            # Evader: maximize distance and move toward farthest corner away from pursuer.
            far_corner = min(corners, key=lambda c: dist2(ox, oy, sx, sy))  # corner currently "bad" for evader
            fx, fy = far_corner
            dcorner = cheb(nx, ny, fx, fy)
            # For evader we want to move away from the "bad" corner of the pursuer influence.
            score = (d * 100000) + (dcorner * 30) + (step * 5)
            score += abs(nx - ox) + abs(ny - oy) * 0.001
            if score < best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        # Deterministic fallback: stay if no legal move (shouldn't happen often).
        return [0, 0]
    return best