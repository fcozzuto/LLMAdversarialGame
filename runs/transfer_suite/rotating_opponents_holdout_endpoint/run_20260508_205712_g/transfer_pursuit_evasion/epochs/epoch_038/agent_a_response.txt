def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in role) or (("pursuer" in opp_role) and ("evader" not in role))
    if ("evader" in role) and ("pursuer" not in role):
        pursuer = False

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if pursuer:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            tie = (d, cheb(nx, ny, sx, sy), dx, dy)
            if best is None or tie < best[0]:
                best = (tie, [dx, dy])
        return best[1] if best is not None else [0, 0]
    else:
        # Evader: maximize distance; also bias toward farthest corner.
        target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        tcx, tcy = target_corner
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            cd = cheb(nx, ny, tcx, tcy)
            # Prefer farther from pursuer; then farther into chosen corner direction; then smaller step for determinism.
            tie = (-d, -cd, dx, dy)
            if best is None or tie < best[0]:
                best = (tie, [dx, dy])
        return best[1] if best is not None else [0, 0]