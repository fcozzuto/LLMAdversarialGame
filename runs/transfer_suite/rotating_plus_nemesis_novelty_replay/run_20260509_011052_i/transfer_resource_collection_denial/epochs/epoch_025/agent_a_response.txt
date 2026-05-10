def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_value(px, py):
        best = None
        bestv = None
        for rx, ry in resources:
            st = cheb((px, py), (rx, ry))
            ot = cheb((ox, oy), (rx, ry))
            # Prefer resources we can take first, and maximize (opponent_time - our_time).
            # If equal, prefer closer and "more-central" (less cornery) deterministically.
            can_take = 1 if st < ot else (0.5 if st == ot else 0.0)
            v = can_take * 1000 + (ot - st) * 10 - (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.01 - st * 0.1
            if bestv is None or v > bestv:
                bestv = v
                best = (rx, ry, st, ot)
        return bestv

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = best_value(nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]