def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Prefer deterministic tie-breaking: fixed move order already.
    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            score = -10**18
        else:
            # obstacle pressure
            pen = 0
            for bx, by in blocked:
                d2 = dist2(nx, ny, bx, by)
                if d2 == 0:
                    pen += 10**9
                elif d2 == 1:
                    pen += 6
                elif d2 == 2:
                    pen += 2

            # mobility (avoid trapping)
            free = 0
            for mx, my in moves:
                tx, ty = nx + mx, ny + my
                if inb(tx, ty) and (tx, ty) not in blocked:
                    free += 1

            # core pursuit/evasion objective
            d2o = dist2(nx, ny, ox, oy)
            if is_evader:
                core = d2o  # maximize distance
                score = core * 10 + free - pen * 3
            else:
                core = -d2o  # minimize distance
                score = core * 10 + free * 2 - pen * 3

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]