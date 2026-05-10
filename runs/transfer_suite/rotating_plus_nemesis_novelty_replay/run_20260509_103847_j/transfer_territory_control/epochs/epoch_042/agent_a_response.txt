def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                selfT.add((x, y))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opT.add((x, y))

    unT = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = unT[:] if unT else list(opT)
    tx0 = (w - 1) // 2
    ty0 = (h - 1) // 2

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            score = float("-inf")
        else:
            s = 0
            if (nx, ny) in opT:
                s += 14
            elif (nx, ny) in selfT:
                s += 2
            else:
                s += 6  # unclaimed (or otherwise)
            if targets:
                d = 10**9
                for t in targets:
                    dd = dist((nx, ny), t)
                    if dd < d:
                        d = dd
                s += max(0, 10 - d)
            else:
                s += max(0, 6 - dist((nx, ny), (tx0, ty0)))
            if dx == 0 and dy == 0:
                s -= 1
            score = s
        if score > best[0] or (score == best[0] and (dx, dy) == (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]