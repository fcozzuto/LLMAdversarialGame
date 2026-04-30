def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_t = None
        best_val = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where opponent is farther, but still make progress.
            val = (od - sd) * 100 - sd
            if best_val is None or val > best_val or (val == best_val and sd < cheb(sx, sy, rx, ry)):
                best_val = val
                best_t = (rx, ry)

        tx, ty = best_t
        best_move = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            sd2 = cheb(nx, ny, tx, ty)
            # After moving, estimate whether we keep the tempo versus opponent.
            od_to = cheb(ox, oy, tx, ty)
            # small bias to keep moving closer overall
            score = (od_to - sd2) * 1000 - sd2
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move to maximize distance from opponent (deterministic)
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        score = dist * 10 + (dx == 0 and dy == 0) * (-1)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]