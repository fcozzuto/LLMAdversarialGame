def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "escape", "coward"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_adj(x, y):
        cnt = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    cnt += 1
        return cnt

    def target_corner():
        # Choose corner farthest from opponent, bias evader toward it
        best = corners[0]
        bestd = -1
        for c in corners:
            d = cheb(c[0], c[1], ox, oy)
            if d > bestd:
                bestd = d
                best = c
        return best

    tc = target_corner()

    # One-step lookahead: pursuer minimizes distance; evader maximizes distance + heads to corner.
    best_move = moves[0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            # Engine may keep in place if invalid; emulate by staying
            nx, ny = sx, sy

        dist = cheb(nx, ny, ox, oy)
        adj = obstacle_adj(nx, ny)

        if is_evader:
            corner_dist = cheb(nx, ny, tc[0], tc[1])
            # Prefer larger separation from pursuer, then larger distance from target corner (to delay leaving corridor),
            # but also progress toward target corner: net combo.
            score = (dist * 10) + (corner_dist * 0.1) - (adj * 2)
            # also strongly avoid being too close
            score += -1000 if dist <= 1 else 0
        else:
            score = (-dist * 10) - (adj * 2)
            # discourage moves that would accidentally get closer after collision
            score += 5 if dist >= 4 else 0

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]