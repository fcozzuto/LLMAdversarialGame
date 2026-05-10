def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    evade = ("evader" in role) or ("runner" in role)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst(x, y):
        n = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if (x + i, y + j) in blocked:
                    n += 1
        return n

    def boundary_score(x, y):
        dL, dR = x, (w - 1 - x)
        dB, dT = y, (h - 1 - y)
        d = dL
        if dR < d: d = dR
        if dB < d: d = dB
        if dT < d: d = dT
        return d

    best_dx, best_dy = 0, 0
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in blocked:
                continue
            dist = cheb(nx, ny, ox, oy)
            nb = near_obst(nx, ny)
            bd = boundary_score(nx, ny)
            # If evading: maximize distance and boundary safety; else minimize distance and avoid obstacles/boundary.
            val = (dist if evade else -dist)
            val += (1.2 * bd if evade else 0.6 * bd)
            val -= (1.8 * nb)
            if best_val is None or (val > best_val):
                best_val = val
                best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]