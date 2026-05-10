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
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def obst_penalty(nx, ny):
        best = 10**9
        for (x, y) in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
        if best == 10**9:
            return 0.0
        if best == 0:
            return 1e6
        if best <= 1:
            return 25.0
        if best == 2:
            return 8.0
        return float(best) * 0.2

    best_move = (0, 0)
    best_score = -1e18 if pursuer else 1e18

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        # Small deterministic tie-breaker: prefer lower dx then lower dy.
        tie = (dx + 2) * 3 + (dy + 2)

        if pursuer:
            # Capture quickly, but avoid obstacles that can stall.
            score = (-d_to_opp * 10.0) - obst_penalty(nx, ny) - tie * 0.01
            if d_to_opp == 0:
                score += 1e5
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # Evade: maximize distance while staying away from obstacles.
            score = (d_to_opp * 10.0) - obst_penalty(nx, ny) - tie * 0.01
            if d_to_opp == 0:
                score -= 1e5
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]