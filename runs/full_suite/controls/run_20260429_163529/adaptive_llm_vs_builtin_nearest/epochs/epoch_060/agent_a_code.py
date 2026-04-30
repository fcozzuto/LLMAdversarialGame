def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def bfs_dist(start):
        INF = 10**9
        dist = {(start[0], start[1]): 0}
        q = [(start[0], start[1], 0)]
        head = 0
        while head < len(q):
            x, y, d = q[head]
            head += 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    nd = d + 1
                    if nd > 64:
                        continue
                    if (nx, ny) not in dist or nd < dist[(nx, ny)]:
                        dist[(nx, ny)] = nd
                        q.append((nx, ny, nd))
        return dist

    sd = bfs_dist((sx, sy))
    od = bfs_dist((ox, oy))

    best = None
    bestkey = None
    for rx, ry in resources:
        ds = sd.get((rx, ry), 10**9)
        do = od.get((rx, ry), 10**9)
        if ds >= 10**9:
            continue
        # Prefer targets we can reach sooner; if tied, go closer to finish; avoid giving opponent big gap.
        key = (do - ds, -ds, -rx, -ry)
        if bestkey is None or key > bestkey:
            bestkey = key
            best = (rx, ry)
    if best is None:
        best = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))

    rx, ry = best
    cur_ds = sd.get((sx, sy), 10**9)
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nds = bfs_dist((nx, ny)).get((rx, ry), 10**9)
        if nds == 10**9:
            continue
        # Tie-break: also try not to worsen opponent's access to the same target.
        ndo = od.get((rx, ry), 10**9)
        # Slight preference to reduce our distance overall even if target distance is equal.
        moves.append((nds - ndo, nds, abs(nx - rx) + abs(ny - ry), nx, ny, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return [int(moves[0][-2]), int(moves[0][-1])]