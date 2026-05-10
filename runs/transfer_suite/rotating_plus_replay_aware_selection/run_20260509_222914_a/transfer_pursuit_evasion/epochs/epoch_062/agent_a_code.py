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

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def obstacle_risk(x, y):
        if (x, y) in obstacles:
            return 10**7
        risk = 0
        for bx, by in obstacles:
            m = abs(x - bx) + abs(y - by)
            if m == 0: risk += 10**6
            elif m == 1: risk += 2500
            elif m == 2: risk += 700
            elif m <= 4: risk += 120
        return risk

    best_move = (0, 0)
    best_score = None

    # Tie-breakers: prefer reducing (or increasing) distance, and also keep closer to center when evading.
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        base = cheb(nx, ny, ox, oy)
        # Pursuer: minimize distance; Evader: maximize distance.
        dist_score = base if is_pursuer else -base

        cx = abs(nx - center_x)
        cy = abs(ny - center_y)
        center_score = cx + cy
        # Pursuer slightly prefers center; evader prefers edges to maintain separation (wall-run style).
        edge_bias = (nx in (0, w - 1)) + (ny in (0, h - 1))
        center_score = center_score if is_pursuer else -edge_bias * 2.0 + center_score * 0.1

        stay_pen = 10 if (dx == 0 and dy == 0) else 0
        risk = obstacle_risk(nx, ny)

        score = dist_score + center_score + stay_pen + risk
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]