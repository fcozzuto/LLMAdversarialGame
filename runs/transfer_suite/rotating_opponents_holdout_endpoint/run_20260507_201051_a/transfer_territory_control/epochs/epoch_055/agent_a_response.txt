def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    raw_ob = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in raw_ob)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    # Deterministic frontier target: nearest unclaimed reachable from our territory (or from center if none)
    targets = list(unclaimed)
    if not targets:
        targets = [ (w//2, h//2) ]
    tx, ty = min(targets, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))

    # Prefer also pressing toward opponent territory if it is adjacent to valuable frontier
    opp_targets = list(oppT)[:]
    if opp_targets:
        ox2, oy2 = min(opp_targets, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))
    else:
        ox2, oy2 = ox, oy

    def adjacent_obstacle_pen(nx, ny):
        pen = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            axx, ayy = nx+ax, ny+ay
            if not (0 <= axx < w and 0 <= ayy < h) or (axx, ayy) in obstacles:
                pen += 1
        return pen

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 7
            val -= 2 * (abs(nx - tx) + abs(ny - ty))
        elif (nx, ny) in oppT:
            val += 4
            val -= 1 * (abs(nx - ox2) + abs(ny - oy2))
        elif (nx, ny) in selfT:
            val += 2
            val -= 1 * (abs(nx - tx) + abs(ny - ty))
        else:
            val += 0
            val -= 2 * (abs(nx - tx) + abs(ny - ty))

        val -= 0.6 * adjacent_obstacle_pen(nx, ny)

        # Small deterministic bias toward moving closer to (tx,ty)
        val += 0.01 * (-(abs(nx - tx) + abs(ny - ty)))

        if val > best_val or (val == best_val and (nx, ny) < best):
            best_val = val
            best = (nx, ny)

    if best is None:
        return [0, 0]
    return [best[0] - sx, best[1] - sy]