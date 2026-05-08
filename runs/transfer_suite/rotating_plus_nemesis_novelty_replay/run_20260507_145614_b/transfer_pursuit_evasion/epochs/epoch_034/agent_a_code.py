def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d2 = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)
        if evader:
            # maximize survival: maximize distance; slightly prefer moves that reduce approach via obstacles
            min_obst = 10**9
            for bx, by in obst:
                if bx == nx and by == ny:
                    min_obst = -1
                    break
                min_obst = min(min_obst, abs(nx - bx) + abs(ny - by))
            score = (d2 * 1000) + (min_obst if min_obst < 10**9 else 0) - man
            # tie-break: deterministic preference order already in dirs
            if best is None or score > best:
                best = score
                best_move = [dx, dy]
        else:
            # pursuer: minimize distance; prioritize immediate capture
            if nx == ox and ny == oy:
                best_move = [dx, dy]
                return best_move
            # obstacle-aware greediness
            min_obst = 10**9
            for bx, by in obst:
                min_obst = min(min_obst, abs(nx - bx) + abs(ny - by))
            score = (-man * 1000) - (d2) + (min_obst if min_obst < 10**9 else 0)
            if best is None or score > best:
                best = score
                best_move = [dx, dy]

    return best_move