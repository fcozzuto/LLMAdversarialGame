def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in role_self) or ("chaser" in role_self) or ("hunter" in role_self) or ("pursuit" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Penalty for moving adjacent to obstacles to reduce obstacle hits on zigzags
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_pen += 1
        # Deterministic tie-break: prefer higher d when evading, lower d when pursuing; then prefer (dx,dy) order.
        val = (-d if is_pursuer else d) - 0.01 * adj_pen
        if best is None or val < best_val:
            best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]

    # If evader and multiple equal best values collapse due to float, make final deterministic move away in axis order.
    if not is_pursuer:
        # prefer increasing Chebyshev distance: evaluate again deterministically among all legal moves
        legal = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and not blocked(nx, ny):
                legal.append((dx, dy))
        bestd = -1
        pick = (0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, ox, oy)
            if d > bestd or (d == bestd and (dx, dy) < pick):
                bestd = d
                pick = (dx, dy)
        best = pick

    return [int(best[0]), int(best[1])]