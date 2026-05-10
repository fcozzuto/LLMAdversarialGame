def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in blocked

    targets = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                targets.add((x, y))
    if not targets:
        for p in observation.get("resources") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    targets.add((x, y))
    if not targets and observation.get("opponent_territory"):
        for p in observation.get("opponent_territory") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    targets.add((x, y))
    if not targets:
        targets = {(ox, oy)}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dmin = 10**18
        for tx, ty in targets:
            d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            if d < dmin:
                dmin = d
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = -dmin * 100 - dist_opp
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]