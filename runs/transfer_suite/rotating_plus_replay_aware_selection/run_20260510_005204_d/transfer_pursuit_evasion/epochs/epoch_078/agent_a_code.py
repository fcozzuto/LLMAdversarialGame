def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    evader = ("evader" in role) or ("runner" in role) or ("evade" in role)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def adj_obst(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in blocked:
                c += 1
        return c

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        # Objective: pursuer minimizes distance; evader maximizes.
        obj = d2 if evader else -d2
        # Wall-hug penalty/bonus to avoid getting pinned; evader prefers staying away, pursuer prefers tight corridors.
        a = adj_obst(nx, ny)
        wall_term = (a if evader else -a)
        # Secondary tie-break: keep moves deterministic and avoid drift toward closer obstacles on both sides.
        turn = (dx + 2) * 10 + (dy + 2)
        score = obj * 1000 + wall_term * 10 - turn
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]