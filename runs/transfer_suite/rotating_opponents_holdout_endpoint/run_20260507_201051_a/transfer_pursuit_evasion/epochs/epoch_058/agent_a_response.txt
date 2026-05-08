def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in self_role) and ("evad" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def obstacle_pen(x, y):
        if not obstacles:
            return 0
        # Strongly discourage landing on/next to obstacles, but allow stepping around them.
        if (x, y) in obstacles:
            return 20
        best = 999
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        if best == 0:
            return 20
        if best == 1:
            return 8
        if best == 2:
            return 3
        return 0

    # If tie, prefer moves that advance (pursuer) or retreat (evader) more in Chebyshev metric.
    def metric(x, y):
        return max(abs(x - ox), abs(y - oy))

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        d = metric(nx, ny)
        pen = obstacle_pen(nx, ny)

        # Wall-run feel: also discourage getting "stuck" by penalizing moves that keep you
        # very close to obstacles while not increasing (evader) / decreasing (pursuer) distance.
        # Use sign by role.
        if is_pursuer:
            # want smaller d
            score = (-d) * 10 + (-pen) * 2
            # slight bias to not move away from opponent
            score += (0 if d == metric(sx, sy) else 0.1 if d < metric(sx, sy) else -0.1)
        else:
            # want larger d
            score = (d) * 10 + (-pen) * 2
            score += (0 if d == metric(sx, sy) else 0.1 if d > metric(sx, sy) else -0.1)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-breaker: lexicographic on (dx,dy) after secondary by metric improvement
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]