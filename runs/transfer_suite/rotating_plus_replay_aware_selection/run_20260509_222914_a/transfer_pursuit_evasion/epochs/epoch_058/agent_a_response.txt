def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def min_obstacle_dist(x, y):
        if not obstacles:
            return 10
        m = 10**9
        for (bx, by) in obstacles:
            d = abs(x - bx) + abs(y - by)
            if d < m:
                m = d
        return m

    def apply_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            return sx, sy
        if (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    best = None
    best_score = None

    for dx, dy in moves:
        x1, y1 = apply_move(dx, dy)
        d1 = abs(x1 - ox) + abs(y1 - oy)
        free1 = min_obstacle_dist(x1, y1)

        # 2-step lookahead: pursue reduces distance, evade increases distance
        best_second = -10**18 if is_pursuer else -10**18
        for ddx, ddy in moves:
            x2, y2 = (x1 + ddx, y1 + ddy)
            if not (0 <= x2 < w and 0 <= y2 < h) or (x2, y2) in obstacles:
                x2, y2 = x1, y1
            d2 = abs(x2 - ox) + abs(y2 - oy)
            free2 = min_obstacle_dist(x2, y2)
            s2 = (-d2 if is_pursuer else d2) + (0.12 * free2)
            # deterministic opponent model: assume worst for our goal (for pursuer, opponent tries to maximize; vice versa)
            if is_pursuer:
                if s2 > best_second:
                    best_second = s2
            else:
                if s2 < best_second:
                    best_second = s2

        s1 = (-d1 if is_pursuer else d1) + (0.10 * free1)
        score = s1 + (0.35 * best_second)

        # Tie-break deterministically: prefer staying diagonal/progress in same direction, then lower dx, then lower dy
        progress = (abs(x1 - sx) + abs(y1 - sy))
        tie = (progress, -dx, -dy)

        if best is None or score > best_score or (score == best_score and tie > best[2]):
            best = [dx, dy, tie]
            best_score = score

    return [best[0], best[1]]