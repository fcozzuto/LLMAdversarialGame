def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    targets = []
    for k in ("unclaimed_cells", "resources", "remaining_resources"):
        if observation.get(k):
            for p in observation.get(k) or []:
                if p and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if ok(x, y) and (x, y) != (sx, sy):
                        targets.append((x, y))
            if targets:
                break
    if not targets:
        tx, ty = ox, oy
    else:
        tx, ty = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - ox) + abs(t[1] - oy), t[0], t[1]))

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        val = (-d_to) + (0.2 * d_opp)
        if val > bestv or (val == bestv and (dx, dy) < (best[0], best[1])):
            bestv = val
            best = [dx, dy]
    return best