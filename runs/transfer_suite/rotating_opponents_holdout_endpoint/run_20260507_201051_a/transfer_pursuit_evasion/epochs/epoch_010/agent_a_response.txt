def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    w = max(1, w); h = max(1, h)

    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_role = str(observation.get("self_role", "pursuer")).lower()
    is_evader = (self_role == "evader")

    # Deterministic tie-break order: already ordered in moves.
    best_move = [0, 0]
    if is_evader:
        # Prefer farthest corner reachable in one step (avoid obstacles), then maximize distance.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = None
        best_corner_d = -1
        for cx, cy in corners:
            if free(cx, cy):
                d = cheb(ox, oy, cx, cy)
                if d > best_corner_d:
                    best_corner_d = d
                    target = (cx, cy)

        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist_to_p = cheb(nx, ny, ox, oy)
            score = dist_to_p * 10
            if target is not None:
                score += cheb(nx, ny, target[0], target[1])
            # Avoid wasting moves that move toward pursuer.
            score -= cheb(sx, sy, ox, oy) * 0.5 if cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy) else 0
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        # Pursuer: minimize distance to evader, while avoiding obstacles.
        best_score = 10**9
        d0 = cheb(sx, sy, ox, oy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist_to_e = cheb(nx, ny, ox, oy)
            # Primary: smaller distance; Secondary: reduce distance improvement negativity; Tertiary: deterministic.
            score = dist_to_e * 10
            if dist_to_e > d0:
                score += 50
            if score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]