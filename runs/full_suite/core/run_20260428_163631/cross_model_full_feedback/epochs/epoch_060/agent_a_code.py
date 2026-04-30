def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Heuristic: move to a resource where we gain distance advantage over opponent,
    # while also drifting away from opponent and slightly toward board center.
    def man(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    me = (sx, sy)
    opp = (ox, oy)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        new_me = (nx, ny)
        base_center = -((nx - cx) ** 2 + (ny - cy) ** 2)

        if resources:
            best_local = -10**18
            for rx, ry in resources:
                myd = man(new_me, (rx, ry))
                od = man(opp, (rx, ry))
                # Prefer positions where we become closer than opponent; still seek low myd.
                # Also reward reducing absolute competition gap.
                gap = myd - od
                local = (-myd) + (0.9 * od) - (2.2 * gap) + (-0.08 * (myd * myd))
                if local > best_local:
                    best_local = local
            score = best_local + 0.35 * base_center
        else:
            # If no resources visible, just move away from opponent while keeping center pressure.
            score = (1.8 * man(new_me, opp)) + 0.35 * base_center

        # Safety: avoid getting too close to opponent.
        score -= 2.0 / (1 + man(new_me, opp))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]