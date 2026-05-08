def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    self_role = (observation.get("self_role") or "")
    i_am_pursuer = ("pursuer" in self_role.lower()) or (self_role.lower() == "pursuer")

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # minimax depth-1 (deterministic): choose our move that optimizes worst-case next distance
    best_val = None
    best_mv = (0, 0)
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not inb(nsx, nsy):
            continue
        # Capture is unlikely with radius 0; still handle robustly.
        if i_am_pursuer and cheb(nsx, nsy, ox, oy) == 0:
            return [dx, dy]

        # Opponent best-response (for that next state).
        max_dist = None
        min_dist = None
        for odx, ody in moves:
            nox, noy = ox + odx, oy + ody
            if not inb(nox, noy):
                continue
            d = cheb(nsx, nsy, nox, noy)
            if i_am_pursuer:
                # Opponent is evader: maximize distance from us.
                if max_dist is None or d > max_dist:
                    max_dist = d
            else:
                # We are evader: opponent is pursuer: minimize distance from us.
                if min_dist is None or d < min_dist:
                    min_dist = d

        if i_am_pursuer:
            val = max_dist if max_dist is not None else cheb(nsx, nsy, ox, oy)
            # tie-breaker: prefer moves that also reduce distance to keep pressure
            # (minimize val first, then minimize direct distance)
            direct = cheb(nsx, nsy, ox, oy)
            key = (val, direct, -dx, -dy)
            if best_val is None or key < best_val:
                best_val = key
                best_mv = (dx, dy)
        else:
            val = min_dist if min_dist is not None else cheb(nsx, nsy, ox, oy)
            # Evader: maximize worst-case distance
            direct = cheb(nsx, nsy, ox, oy)
            key = (-val, -direct, dx, dy)
            if best_val is None or key < best_val:
                best_val = key
                best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]