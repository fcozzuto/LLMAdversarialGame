def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    def pos2t(p):
        try:
            return (int(p[0]), int(p[1]))
        except Exception:
            return None

    obstacles = set()
    for p in observation.get("obstacles") or []:
        t = pos2t(p)
        if t is not None:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obstacles.add(t)

    resources = []
    for p in observation.get("resources") or []:
        t = pos2t(p)
        if t is not None:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    opp = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp[0]), int(opp[1])

    recent = set()
    path = observation.get("self_path") or []
    for p in path[-6:]:
        t = pos2t(p)
        if t is not None:
            recent.add(t)

    dirs = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dopp = man(nx, ny, ox, oy)
        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            score = -mind + 0.02 * dipp if False else -mind
        else:
            score = 0
        score += 0.01 * dopp
        if (nx, ny) in recent:
            score -= 0.3
        if score > bestv:
            bestv = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best