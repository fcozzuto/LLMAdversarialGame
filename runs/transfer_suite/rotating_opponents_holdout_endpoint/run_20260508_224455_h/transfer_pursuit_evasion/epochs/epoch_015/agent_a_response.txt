def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    evader_keys = ("evader", "evade", "escape", "runner", "evasion")
    we_evade = any(k in role for k in evader_keys) and not any(k in opp_role for k in evader_keys)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    near_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def score(nx, ny):
        # Prefer staying mobile away from obstacles.
        nbh = 0
        for dx2 in (-1, 0, 1):
            for dy2 in (-1, 0, 1):
                if dx2 == 0 and dy2 == 0:
                    continue
                x2, y2 = nx + dx2, ny + dy2
                if inb(x2, y2) and not blocked(x2, y2):
                    nbh += 1
        # Main objective: pursue (minimize) or evade (maximize) distance.
        d = manh(nx, ny)
        if we_evade:
            c = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            t = abs(nx - near_corner[0]) + abs(ny - near_corner[1])
            return (d, -c, nbh, -t)  # maximize d, also run toward far corner
        else:
            c = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            t = abs(nx - near_corner[0]) + abs(ny - near_corner[1])
            # minimize d; tie-break: move away from far corner and toward near corner
            return (-d, c, nbh, t)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        sc = score(nx, ny)
        if best is None or sc > best or (sc == best and (dx, dy) < tuple(best_move)):
            best = sc
            best_move = [dx, dy]
    return best_move