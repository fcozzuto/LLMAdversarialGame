def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    opp = (ox, oy)
    me = (sx, sy)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target_from(pos):
        if resources:
            bestd = None
            for t in resources:
                d = man(pos, t)
                if bestd is None or d < bestd:
                    bestd = d
            return bestd if bestd is not None else 0
        cx, cy = w // 2, h // 2
        return man(pos, (cx, cy))

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = me[0] + dx, me[1] + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        tdist = best_target_from((nx, ny))
        odist = man((nx, ny), opp)
        score = -tdist * 1000 - odist
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]