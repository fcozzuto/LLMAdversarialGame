def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", None) or [0, 0]
    op = observation.get("opponent_position", None) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", None) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", None) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = sorted(dirs, key=lambda d: (d[0] * 3 + d[1] + 5))  # deterministic

    def best_for(x, y):
        if resources:
            best_res = min((cheb(x, y, rx, ry) for rx, ry in resources), default=10**9)
            # Prefer moving toward resources that are also not closer for opponent.
            opp_penalty = 0
            if resources:
                best_opp = min((cheb(ox, oy, rx, ry) for rx, ry in resources), default=10**9)
                if best_res >= best_opp:
                    opp_penalty = 1
            return best_res + opp_penalty
        return 0

    best_move = [0, 0]
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        score = best_for(nx, ny)
        if score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move