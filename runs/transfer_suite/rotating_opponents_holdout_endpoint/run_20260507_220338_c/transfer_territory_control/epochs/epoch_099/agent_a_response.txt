def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj4(x, y, T):
        return (x - 1, y) in T or (x + 1, y) in T or (x, y - 1) in T or (x, y + 1) in T

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target preference: nearest unclaimed; if none, nearest opponent territory cell
    targets = list(unclaimed)
    if not targets:
        targets = list(oppT) if oppT else [(ox, oy)]

    def nearest_dist(x, y):
        bd = 10**9
        for tx, ty in targets:
            d = man(x, y, tx, ty)
            if d < bd:
                bd = d
        return bd

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        p = (nx, ny)

        # Base: move closer to a target
        dist = nearest_dist(nx, ny)
        v = -dist

        # Territory intent
        if p in unclaimed:
            v += 2.5
        if p in oppT:
            v += 3.0  # flip on entry enabled
        if p in selfT:
            v += 0.2

        # Frontier shaping: encourage adjacency to our territory and to contested boundary
        v += 0.35 * (adj4(nx, ny, selfT) or False)
        v += 0.6 if (p not in selfT and ((nx - 1, ny) in selfT or (nx + 1, ny) in selfT or (nx, ny - 1) in selfT or (nx, ny + 1) in selfT)) else 0.0
        v += 0.4 if (p not in oppT and ((nx - 1, ny) in oppT or (nx + 1, ny) in oppT or (nx, ny - 1) in oppT or (nx, ny + 1) in oppT)) else 0.0

        # Tie-break deterministically toward forward-ish direction (towards opponent)
        v += 0.001 * (man(nx, ny, ox, oy) == 0)

        if v > bestv:
            bestv = v
            best_move = [dx, dy]

    return best_move