def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer_like = ("purs" in self_role) or (self_role == "pursuer") or ("purs" in opp_role and "evad" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obs_pen(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        # Stronger penalty when adjacent
        return 1000 if best == 0 else (500 if best == 1 else (50 if best == 2 else 0))

    # Choose a farthest corner for evasion as a soft guide to change strategy vs pure chase
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    tx, ty = far_corner if not pursuer_like else (0 if sx > ox else w - 1, 0 if sy > oy else h - 1)

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, tx, ty)

        # Score: pursuer maximizes approach; evader maximizes distance while drifting toward far corner.
        if pursuer_like:
            score = (-d_opp) + 0.02 * d_tgt - obs_pen(nx, ny)
        else:
            score = (d_opp) + 0.02 * d_tgt - obs_pen(nx, ny)

        # Deterministic tie-break: prefer lexicographically smaller (dx,dy) among equals.
        item = (score, -dx, -dy)
        if best is None or item > best:
            best = item
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]