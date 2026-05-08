def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [None, None])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    targets = []
    res = observation.get("resources")
    if res is not None:
        for p in (res or []):
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obs:
                    targets.append((x, y))
    if not targets:
        for p in (observation.get("unclaimed_cells") or []):
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obs:
                    targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if targets:
            mind = None
            for tx, ty in targets:
                d = abs(nx - tx) + abs(ny - ty)
                if mind is None or d < mind:
                    mind = d
            score = -mind if mind is not None else 0
        if ox is not None and oy is not None:
            # small tie-break: keep some distance from opponent
            score += (abs(nx - int(ox)) + abs(ny - int(oy))) * 0.001
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    # fallback: any in-bounds non-obstacle move; else stay
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
        nx, ny = int(sx + dx), int(sy + dy)
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]