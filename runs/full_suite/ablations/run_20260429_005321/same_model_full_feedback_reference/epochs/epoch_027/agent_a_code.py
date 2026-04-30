def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        v = a - c
        if v < 0:
            v = -v
        t = b - d
        if t < 0:
            t = -t
        return v + t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            # race-heuristic: pick resource that maximizes (opp farther - self closer)
            best = -10**9
            for rx, ry in resources:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                # Prefer immediate pickup, then better race position, also slightly reduce total distance
                v = 0
                if ds == 0:
                    v += 1000
                # If we can get there sooner (or opponent needs longer), increase score
                # Use difference with small tie-break using distances
                v += (do - ds) * 6
                v += (30 - ds) * 0.2
                # Mild repulsion from being too close to opponent (avoid direct contest unless winning)
                v += (-dist(nx, ny, ox, oy)) * 0.02
                if v > best:
                    best = v
            # Extra: discourage stepping into "dead zones" near obstacles by penalizing low mobility
            free = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if legal(tx, ty):
                    free += 1
            best -= (8 - free) * 0.3
            cand.append((best, dx, dy))

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]