def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mindist_to_resources(x, y):
        best = None
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if best is None or d < best:
                best = d
        return best

    tx = None
    ty = None
    bestd = None
    for rx, ry in resources:
        d = abs(rx - sx) + abs(ry - sy)
        if bestd is None or d < bestd:
            bestd, tx, ty = d, rx, ry

    if bestd is None:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            dres = mindist_to_resources(nx, ny)
            opp_after = abs(ox - nx) + abs(oy - ny)
            score = (-dres, opp_after)
        else:
            dopp = abs(ox - nx) + abs(oy - ny)
            score = (-dopp, 0)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]