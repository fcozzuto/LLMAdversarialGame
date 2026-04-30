def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        target = min(resources, key=lambda r: (dist((sx, sy), r), r[0], r[1]))
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), target)
        # small anti-stall/anti-approach opponent pressure
        score = (d, 0 if (nx, ny) == target else 1, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is not None:
        return [int(best[1]), int(best[2])]

    # Fallback: stay if possible else first valid adjacent
    if 0 <= sx < w and 0 <= sy < h and (sx, sy) not in obstacles:
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [0, 0]