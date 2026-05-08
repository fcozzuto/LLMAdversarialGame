def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(t) for t in (observation.get("self_territory") or []))
    oppT = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(x, y, T):
        cnt = 0
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in T:
                cnt += 1
        return cnt

    best = None
    bestv = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_op = abs(nx - ox) + abs(ny - oy)
        # Center priority (deny edge-claim style by going inward)
        center_dist = abs(nx - cx) + abs(ny - cy)

        v = 0
        if (nx, ny) in selfT:
            v += 40
        if (nx, ny) in oppT:
            # flipping on entry is true; take opportunities but don't suicide into opponent pursuit
            v += 120 - 3.0 * dist_op
        if (nx, ny) in unclaimed:
            v += 180 - 2.5 * center_dist

        # Expand contiguously from our territory
        v += 35 * adj_count(nx, ny, selfT)

        # Keep distance from opponent when all else equal
        v += 0.8 * dist_op

        # Slight bias toward moves that reduce center distance (deterministic)
        v += (8.0 - center_dist) * 1.2

        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
        elif v == bestv:
            # deterministic tie-breaker: lexicographically smallest [dx,dy]
            if [dx, dy] < best:
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best