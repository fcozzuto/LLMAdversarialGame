def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    # targets: unclaimed cells first, then resources
    targets = set()
    for key in ("unclaimed_cells", "unclaimed"):
        for p in (observation.get(key) or []):
            if isinstance(p, dict):
                q = p.get("position") or p.get("cell") or p.get("pos")
                if q and len(q) >= 2:
                    targets.add((int(q[0]), int(q[1])))
            else:
                targets.add((int(p[0]), int(p[1])))
    if not targets:
        for p in (observation.get("resources") or []):
            if isinstance(p, dict):
                q = p.get("position") or p.get("cell") or p.get("pos")
                if q and len(q) >= 2:
                    targets.add((int(q[0]), int(q[1])))
            else:
                targets.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    # Score: move toward best target; if no targets, move toward opponent while avoiding obstacles.
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for dx, dy, nx, ny in legal:
        if targets:
            d = min(dist((nx, ny), t) for t in targets)
            # tie-break deterministically: prefer smaller d, then closer to opponent (aggressive), then lexicographic move
            score = (-d, -dist((nx, ny), (ox, oy)), dx, dy)
        else:
            score = (-dist((nx, ny), (ox, oy)), 0, dx, dy)
        if best is None or score > best[0]:
            best = (score, [dx, dy])
    return best[1]