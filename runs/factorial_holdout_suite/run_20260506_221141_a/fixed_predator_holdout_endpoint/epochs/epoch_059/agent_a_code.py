def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except Exception:
            pass
    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    # Prefer resources we can reach earlier than opponent; break ties toward lower self distance and stable coords.
    best = None
    for t in resources:
        sd = cheb((sx, sy), t)
        od = cheb((ox, oy), t)
        denom = sd + od + 1
        # Encourage "win chance" and also avoid being too close to opponent (denier archetype).
        winish = (od - sd) * 1000
        tie_break = -sd * 10 - (abs(t[0]) + abs(t[1])) % 7
        key = (winish, tie_break, -t[0], -t[1], denom)
        if best is None or key > best[0]:
            best = (key, t)
    tx, ty = best[1]

    # Greedy one-step move toward target with obstacle avoidance; deterministic ordering.
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    candidates = []
    # Bias diagonal then axes, but deterministic.
    candidates.extend([(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0), (0, 0)])
    # Remove duplicates while preserving order.
    seen = set()
    ordered = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            ordered.append(c)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_score = None
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate: reduce distance to target; also keep away from opponent slightly.
        self_to = cheb((nx, ny), (tx, ty))
        opp_to = cheb((nx, ny), (ox, oy))
        # If can capture resource now, prioritize strongly.
        capture = 5000 if (nx, ny) == (tx, ty) else 0
        score = (capture + (200 - self_to) + opp_to * 2, -self_to, -opp_to, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]