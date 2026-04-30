def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def score_cell(x, y):
        if not safe(x, y):
            return None
        if resources:
            bestd = None
            bestpos = None
            for rx, ry in resources:
                d = max(abs(x - rx), abs(y - ry))
                if bestd is None or d < bestd or (d == bestd and (ry, rx) < bestpos):
                    bestd = d
                    bestpos = (ry, rx)
            dres = bestd
        else:
            tx, ty = w // 2, h // 2
            dres = max(abs(x - tx), abs(y - ty))
        dob = max(abs(x - ox), abs(y - oy))
        # Prefer getting closer to a resource, while not letting opponent get too close.
        return (dres * 100 - dob, -man(x, y, 0 if sx > ox else w - 1, 0))

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        val = score_cell(nx, ny)
        if val is None:
            continue
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]