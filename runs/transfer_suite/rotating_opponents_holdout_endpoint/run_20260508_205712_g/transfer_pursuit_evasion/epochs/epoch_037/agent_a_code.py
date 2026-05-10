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

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_corner_dist(x, y):
        d = 10**9
        for cx, cy in corners:
            cd = cheb(cx, cy, x, y)
            if cd < d: d = cd
        return d

    # If on capture cell already, stay (deterministic)
    if sx == ox and sy == oy:
        return [0, 0]

    # If pursuer: move to minimize distance to opponent (avoid obstacles)
    # If evader: move to maximize distance to pursuer (also prefer moving away from being trapped)
    best_move = (0, 0)
    if pursuer:
        best_val = 10**9
        best_corner = -1
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            c = best_corner_dist(nx, ny)
            if d < best_val or (d == best_val and c > best_corner):
                best_val = d
                best_corner = c
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        best_val = -1
        best_corner = -1
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            c = best_corner_dist(nx, ny)
            # Prefer larger distance; then prefer being farther from the nearest corner (more space)
            if d > best_val or (d == best_val and c > best_corner):
                best_val = d
                best_corner = c
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]