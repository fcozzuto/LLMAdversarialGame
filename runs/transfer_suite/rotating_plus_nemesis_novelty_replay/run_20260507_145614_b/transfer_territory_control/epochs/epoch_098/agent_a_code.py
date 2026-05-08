def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [None, None])
    sx, sy = int(sx), int(sy)
    ox = int(ox) if ox is not None else None
    oy = int(oy) if oy is not None else None

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    targets = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))
    if not targets:
        for p in (observation.get("resources") or []):
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))
    if not targets and ox is not None and oy is not None:
        targets = [(ox, oy)]
    if not targets:
        targets = [(w // 2, h // 2)]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    tx, ty = targets[0]
    bestd = None
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if bestd is None or d < bestd:
            bestd, tx, ty = d, x, y

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in opp_terr:
            v -= 100000
        v -= abs(tx - nx) + abs(ty - ny)
        if ox is not None and oy is not None:
            v += -0.1 * (abs(ox - nx) + abs(oy - ny))
        if bestv is None or v > bestv:
            bestv, best = v, (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]