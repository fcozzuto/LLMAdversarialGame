def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources", []) or [])]
    resources = [p for p in resources if p not in obstacles]

    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or [])]
    unclaimed = [p for p in unclaimed if p not in obstacles]

    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target_list = resources if resources else unclaimed
    if target_list:
        target = min(target_list, key=lambda q: (dist((sx, sy), q), q[0], q[1]))
    else:
        target = (w // 2, h // 2)

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), target)
        score = -d
        if (nx, ny) in opp_terr:
            score += 3
        if (nx, ny) in self_terr:
            score -= 1
        score += -dist((nx, ny), (px, py)) * 0.01
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]