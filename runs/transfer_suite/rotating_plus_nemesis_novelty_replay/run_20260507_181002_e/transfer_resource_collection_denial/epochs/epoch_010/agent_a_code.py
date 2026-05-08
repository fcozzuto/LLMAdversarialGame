def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) == 2:
            obs.add((p[0], p[1]))
    resources = observation.get("resources", []) or []
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        # Chebyshev distance suits diagonal moves
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]

    # If no resources visible, drift to reduce opponent advantage (toward them if close, else hold)
    if not resources:
        if dist(sx, sy, ox, oy) <= 2:
            tx = ox
            ty = oy
            dx = 0 if tx == sx else (1 if tx > sx else -1)
            dy = 0 if ty == sy else (1 if ty > sy else -1)
            return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        # Prefer stepping that makes us strictly closer than opponent to some resource,
        # and if tie, prefer fewer self steps and farther-from-opponent.
        best_local = None
        for r in resources:
            if r is None or len(r) != 2:
                continue
            tx, ty = r
            if (tx, ty) in obs:
                continue
            if (tx, ty) == (nx, ny):
                self_d = 0
                opp_d = dist(ox, oy, tx, ty)
            else:
                self_d = dist(nx, ny, tx, ty)
                opp_d = dist(ox, oy, tx, ty)
            gain = opp_d - self_d  # positive means we are closer
            # Two-level tuple: maximize gain, then minimize self_d, then maximize opp_d
            cand = (gain, -self_d, opp_d)
            if best_local is None or cand > best_local:
                best_local = cand
        if best_local is None:
            continue
        # Small anti-stall: prefer moves that change position unless all equivalent
        val = (best_local, 0 if (dx == 0 and dy == 0) else 1)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]