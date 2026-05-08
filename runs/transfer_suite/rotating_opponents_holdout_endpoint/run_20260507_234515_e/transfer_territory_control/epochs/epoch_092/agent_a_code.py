def choose_move(observation):
    w = observation.get("grid_width", 0) or 8
    h = observation.get("grid_height", 0) or 8
    sx, sy = observation.get("self_position") or (0, 0)
    sx = int(sx); sy = int(sy)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        try:
            x = int(c[0]); y = int(c[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))
        except Exception:
            pass

    selfT = set()
    for c in observation.get("self_territory") or []:
        try:
            selfT.add((int(c[0]), int(c[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    adj_unclaimed = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in set(unclaimed):
            adj_unclaimed.append((nx, ny))
    if adj_unclaimed:
        adj_unclaimed.sort()
        tx, ty = adj_unclaimed[0]
        return [tx - sx, ty - sy]

    if unclaimed:
        target = min(unclaimed, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))
        best = None
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(target[0]-nx) + abs(target[1]-ny)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    best = None
    bestscore = -10**9
    oppd0 = abs(ox - sx) + abs(oy - sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dopp = abs(ox - nx) + abs(oy - ny)
        score = (dopp - oppd0) * 10
        if (nx, ny) in selfT:
            score += 1
        if score > bestscore:
            bestscore = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]