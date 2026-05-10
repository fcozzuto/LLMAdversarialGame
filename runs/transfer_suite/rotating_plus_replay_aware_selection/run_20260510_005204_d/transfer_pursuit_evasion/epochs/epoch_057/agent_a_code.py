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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return (dx if dx >= 0 else -dx) if (dx if dx >= 0 else -dx) > (dy if dy >= 0 else -dy) else (dy if dy >= 0 else -dy)

    def near_obst(x, y):
        n = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if (x + i, y + j) in blocked:
                    n += 1
        return n

    def interior_bias(x, y):
        dL, dR = x, (w - 1 - x)
        dB, dT = y, (h - 1 - y)
        return min(dL, dR, dB, dT)  # larger is better (away from boundary)

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        dist = cheb(nx, ny, ox, oy)
        nb = near_obst(nx, ny)
        ib = interior_bias(nx, ny)

        # deterministic tie-break: prefer (dx,dy) order already in moves list
        if evading:
            score = dist * 1000 + ib * 10 - nb * 50
        else:
            score = -dist * 1000 + ib * 10 - nb * 50

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        # all blocked or invalid: attempt to stay
        return [0, 0]
    return best