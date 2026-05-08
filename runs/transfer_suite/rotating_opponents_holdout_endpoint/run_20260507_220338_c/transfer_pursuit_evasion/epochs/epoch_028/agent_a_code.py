def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("evader" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def bfs_dist(startx, starty, targetx, targety, maxd=6):
        if startx == targetx and starty == targety:
            return 0
        if not ok(startx, starty) or not ok(targetx, targety):
            return 10**9
        qx, qy = [startx], [starty]
        dist = {(startx, starty): 0}
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d = dist[(x, y)]
            if d >= maxd:
                continue
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if ok(nx, ny) and (nx, ny) not in dist:
                    nd = d + 1
                    dist[(nx, ny)] = nd
                    if nx == targetx and ny == targety:
                        return nd
                    qx.append(nx)
                    qy.append(ny)
        return maxd + 1

    best = (10**18, (0, 0))
    # Prefer a small, decisive local policy: chase/flee using obstacle-aware approximate distances.
    # Tie-breaker: deterministic ordering by (dx,dy) index.
    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_approx = bfs_dist(nx, ny, ox, oy, 6)
        score = d_approx if is_evader else -d_approx
        # Make evader also prefer moving away from immediate contact.
        if is_evader:
            score += (bfs_dist(ox, oy, nx, ny, 2) == 1) * (-1000)
        else:
            score += (bfs_dist(nx, ny, ox, oy, 2) == 1) * (1000)
        if score > best[0] or (score == best[0] and i < deltas.index(best[1])):
            best = (score, (dx, dy))

    if best[1] == (0, 0):
        # Fallback if all neighbor cells blocked/out: try staying or any valid step.
        for dx, dy in deltas:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]