def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in (observation.get("obstacles", []) or []):
        try:
            x, y = c
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            x, y = r
            resources.append((int(x), int(y)))
        except Exception:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = man((nx, ny), (ox, oy))
        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < mind:
                    mind = d
        else:
            mind = 0
        score = (-mind) + 0.2 * d_opp
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best, best_score = (dx, dy), score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]