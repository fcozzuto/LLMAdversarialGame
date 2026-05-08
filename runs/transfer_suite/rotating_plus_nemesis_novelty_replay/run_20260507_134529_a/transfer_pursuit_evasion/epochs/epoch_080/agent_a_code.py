def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Evader picks corner farthest from pursuer; pursuer picks closest to evader.
    target_corner = max(corners, key=lambda c: dist(c[0], c[1], ox, oy)) if is_evader else min(corners, key=lambda c: dist(c[0], c[1], ox, oy))
    tcx, tcy = target_corner

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaker order independent of move ordering.
    moves = sorted(moves, key=lambda d: (d[0], d[1]))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_op = dist(nx, ny, ox, oy)
        d_to_corner = dist(nx, ny, tcx, tcy)
        # Evader wants to maximize distance to opponent, and also move toward safe corner.
        # Pursuer wants to minimize distance to opponent, and approach target corner to cut off.
        score = (d_to_op * 1000 + (-d_to_corner if is_evader else d_to_corner))
        if best is None or (is_evader and score > best_score) or ((not is_evader) and score < best_score):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]