def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    self_terr = observation.get("self_territory") or []
    self_set = set()
    for p in self_terr:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))

    opp_set = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    oppp = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(oppp[0]), int(oppp[1])

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if unclaimed:
        target = min(unclaimed, key=lambda t: (man((sx, sy), t), t[0], t[1]))
    elif resources:
        target = min(resources, key=lambda t: (man((sx, sy), t), t[0], t[1]))
    else:
        cand = []
        for (x, y) in self_set:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_set:
                    cand.append((nx, ny))
        if cand:
            target = min(cand, key=lambda t: (man((sx, sy), t), 0 if t in opp_set else 1, t[0], t[1]))
        else:
            target = (ox, oy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, 10**9, 10**9)
    best_d = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(nx - target[0]) + abs(ny - target[1])
        score = d
        # Prefer moving into opponent territory to enable flipping when no better target exists.
        if (nx, ny) in opp_set:
            score -= 0.25
        # Tie-break deterministically
        key = (score, d, dx, dy)
        if key < best:
            best = key
            best_d = (dx, dy)

    return [int(best_d[0]), int(best_d[1])]