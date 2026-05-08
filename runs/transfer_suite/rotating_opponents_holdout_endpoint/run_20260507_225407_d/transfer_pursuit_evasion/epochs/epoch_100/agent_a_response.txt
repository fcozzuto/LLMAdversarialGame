def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "")
    r = role.lower()
    we_pursuer = ("pursuer" in r) or ("pursue" in r and "evader" not in r)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def wall_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    best_move = (0, 0)
    best_val = None

    # If evading, prefer high wall_dist (more room). If pursuing, prefer central-ish.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        wd = wall_dist(nx, ny)

        if we_pursuer:
            # Reduce distance; avoid hugging walls too hard.
            val = (-d * 100) + (wd * 2) + (-(abs(nx - ox) + abs(ny - oy)) * 0.01)
        else:
            # Maximize distance; keep room to maneuver.
            val = (d * 100) + (wd * 3) + (-(abs(nx - ox) + abs(ny - oy)) * 0.01)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]