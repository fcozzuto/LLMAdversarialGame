def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for p in observation.get("resources", []) or []:
        try:
            resources.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            md = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < md:
                    md = d
            res_score = -md
        else:
            res_score = 0

        od = abs(nx - ox) + abs(ny - oy)
        opp_score = od

        score = (res_score * 2) + opp_score
        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best