def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    evading = ("evader" in role) or ("runner" in role)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def near_obst(x, y):
        n = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if (x + i, y + j) in blocked:
                    n += 1
        return n

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        dist = cheb(nx, ny, ox, oy)
        nb = near_obst(nx, ny)
        # interior preference helps avoid getting stuck on boundaries
        interior = min(nx, w - 1 - nx, ny, h - 1 - ny)

        # Capture ends game; if we are pursuer and can capture, prioritize heavily.
        if not evading and dist == 0:
            score = 1e9
        else:
            # If evading: maximize distance; else minimize distance.
            # Also penalize obstacle proximity; reward being more interior.
            base = (-dist if not evading else dist)
            score = base * 1000.0 + interior * 3.0 - nb * (40.0 if evading else 30.0)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]