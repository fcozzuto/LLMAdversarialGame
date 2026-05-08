def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0] * 2 + d[1], d[0], d[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        # add secondary tie-break to avoid standing still when not best
        still_pen = 1 if (dx == 0 and dy == 0) else 0
        val = (d, still_pen, nx + ny)  # deterministic
        if best is None:
            best, best_val = (dx, dy), val
        else:
            if is_evader:
                if val[0] > best_val[0] or (val[0] == best_val[0] and (val[1] < best_val[1] or (val[1] == best_val[1] and val[2] > best_val[2]))):
                    best, best_val = (dx, dy), val
            else:
                if val[0] < best_val[0] or (val[0] == best_val[0] and (val[1] < best_val[1] or (val[1] == best_val[1] and val[2] < best_val[2]))):
                    best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]