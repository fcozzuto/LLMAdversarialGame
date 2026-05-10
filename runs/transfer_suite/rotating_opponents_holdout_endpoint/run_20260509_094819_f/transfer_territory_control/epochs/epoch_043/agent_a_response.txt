def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w-1, h-1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    def nearest_dist(pt, S):
        if not S: return 999
        x, y = pt
        best = 999
        for (sx2, sy2) in S:
            d = abs(x - sx2) + abs(y - sy2)
            if d < best: best = d
        return best

    def adjacent_self(cell):
        x, y = cell
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
            if (x+ax, y+ay) in selfT: return True
        return False

    # Precompute small stats for heuristic
    opp_boundary = set()
    for (x, y) in oppT:
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+ax, y+ay
            if (inb(nx, ny) and (nx, ny) not in oppT): opp_boundary.add((x, y)); break

    best = -10**9
    best_move = [0, 0]
    cx, cy = w // 2, h // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue
        if (nx, ny) in obstacles: continue

        cell = (nx, ny)
        d_opp = nearest_dist(cell, opp_boundary) if opp_boundary else nearest_dist(cell, oppT)
        d_uncla = nearest_dist(cell, uncla) if uncla else 999
        d_center = man(nx, ny, cx, cy)

        if cell in selfT:
            base = 0.2
        elif cell in uncla:
            base = 1.4
        elif cell in oppT:
            base = 2.2
        else:
            base = 0.5

        # Push for frontier expansion while also prioritizing counter-taking near us.
        frontier = 0.8 if adjacent_self(cell) else 0.0
        # Prefer breaking toward opponent cluster but avoid getting too close to heavy counterclaim pressure.
        pressure = -0.35 * d_opp
        # Slightly reduce wandering.
        steer = -0.02 * d_center

        score = base + frontier + pressure + steer + (-0.03 * d_uncla)
        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move