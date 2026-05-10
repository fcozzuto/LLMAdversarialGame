def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a small deterministic target set
    targets = []
    for r in resources:
        if dist(sx, sy, r[0], r[1]) <= 6:
            targets.append(r)
    if not targets:
        for p in unclaimed:
            if dist(sx, sy, p[0], p[1]) <= 6:
                targets.append(p)
    if not targets:
        for p in opp_terr:
            if dist(sx, sy, p[0], p[1]) <= 6:
                targets.append(p)
    if not targets:
        targets = [(w // 2, h // 2)]

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        val = -dist(nx, ny, ox, oy) * 2  # prefer moving away from opponent
        if (nx, ny) in unclaimed:
            val += 120
        if (nx, ny) in opp_terr:
            val += 80
        # Prefer proximity to chosen targets
        md = None
        for tx, ty in targets:
            d = dist(nx, ny, tx, ty)
            if md is None or d < md:
                md = d
        if md is None:
            md = dist(nx, ny, w // 2, h // 2)
        val += (18 - md) * 6
        # Slight bias to stay within grid center to reduce drifting into corners
        val += - (abs(nx - w // 2) + abs(ny - h // 2)) * 0.2
        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]