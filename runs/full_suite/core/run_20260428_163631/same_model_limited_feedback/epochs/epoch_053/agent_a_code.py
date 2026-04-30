def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = max(abs(rx - sx), abs(ry - sy))
            do = max(abs(rx - ox), abs(ry - oy))
            # Prefer resources we can reach sooner; if close, prefer those that keep opponent behind.
            score = (do - ds, -ds, -((rx - sx) ** 2 + (ry - sy) ** 2), -rx, -ry)
            cand = (score, (rx, ry))
            if best is None or cand[0] > best[0]:
                best = cand
        target = best[1]
    else:
        # If no resources visible, head toward center deterministically.
        target = (w // 2, h // 2)

    tx, ty = target
    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return (-10**9, )
        ns = max(abs(tx - nx), abs(ty - ny))
        no = max(abs(tx - ox), abs(ty - oy))
        # Secondary: disrupt opponent by reducing their distance to target less than ours
        # (i.e., prefer moves that keep opponent relatively farther).
        rel = (no - ns)
        return (rel, -ns, -((nx - tx) ** 2 + (ny - ty) ** 2), -nx, -ny, dx, dy)

    # If opponent is very close to the target, try to "shadow" by moving to minimize max-distance to opponent.
    if resources and resources:
        oxds = []
        for rx, ry in resources[:]:
            if (rx, ry) in obstacles:
                continue
            oxds.append((max(abs(rx - ox), abs(ry - oy)), rx, ry))
        if oxds:
            oxds.sort()
            t2 = (oxds[0][1], oxds[0][2])
            tx, ty = t2

    bestm = None
    for dx, dy in dirs:
        sc = move_score(dx, dy)
        if bestm is None or sc > bestm[0]:
            bestm = (sc, (dx, dy))
    return [bestm[1][0], bestm[1][1]]