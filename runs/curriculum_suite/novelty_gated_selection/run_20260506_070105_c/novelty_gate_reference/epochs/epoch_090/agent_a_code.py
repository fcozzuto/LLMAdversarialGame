def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = (None, None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < mind:
                    mind = d
        else:
            mind = 0

        oppd = man(nx, ny, ox, oy)
        score = -mind * 10 - oppd  # favor closer resources; slightly avoid opponent
        key = (score, -dx, -dy)  # deterministic tie-break
        if best[2] < key[0] or (best[2] == key[0] and (best[0] is None or (key[1], key[2]) > (best[0], best[1]))):
            best = (key[1], key[2], key[0])
            best_move = [dx, dy]

    if best[0] is None:
        return [0, 0]
    return best_move