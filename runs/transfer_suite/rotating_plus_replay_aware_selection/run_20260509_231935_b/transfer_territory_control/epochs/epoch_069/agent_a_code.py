def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obstacles

    resources = observation.get("resources") or []
    best = None
    bestd = 10**18
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            d = abs(rx - sx) + abs(ry - sy)
            if valid(rx, ry) and d < bestd:
                bestd = d
                best = (rx, ry)

    targets = []
    if best is not None:
        tx, ty = best
        targets.append((tx, ty))
    else:
        targets.append((w // 2, h // 2))

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist_score = 10**12
            for tx, ty in targets:
                dist_score = min(dist_score, abs(tx - nx) + abs(ty - ny))
            opp_dist = abs(ox - nx) + abs(oy - ny)
            cand.append((dist_score, -opp_dist, dx, dy))

    if cand:
        cand.sort()
        _, _, dx, dy = cand[0]
        return [dx, dy]

    if valid(sx, sy):
        return [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and (dx != 0 or dy != 0):
                return [dx, dy]
    return [0, 0]