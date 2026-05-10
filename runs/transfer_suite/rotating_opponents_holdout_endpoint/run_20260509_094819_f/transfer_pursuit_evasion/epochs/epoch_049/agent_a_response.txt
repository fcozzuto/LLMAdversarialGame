def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role") or "")
    pursuer = ("purs" in role.lower()) or (role.lower() == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        # 1-step lookahead: estimate opponent's ability to change distance from their perspective
        future = 0
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not inb(tx, ty):
                continue
            nd = dist2(nx, ny, tx, ty)
            if pursuer:
                # pursuer wants closer; opponent (evader) will try to keep distance large
                future = max(future, nd)
            else:
                # evader wants farther; opponent (pursuer) will try to reduce distance
                future = min(future, nd) if future != 0 else nd

        if pursuer:
            # primary: minimize distance; secondary: avoid moves with very few free neighbors (can be corner-trapped)
            free = 0
            for a, b in moves:
                ex, ey = nx + a, ny + b
                if inb(ex, ey):
                    free += 1
            score = -(d) + 0.15 * free - 0.02 * future
            cmp = (best_score is None) or (score > best_score)
        else:
            free = 0
            for a, b in moves:
                ex, ey = nx + a, ny + b
                if inb(ex, ey):
                    free += 1
            score = d + 0.15 * free + 0.02 * future
            cmp = (best_score is None) or (score > best_score)

        if cmp:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]