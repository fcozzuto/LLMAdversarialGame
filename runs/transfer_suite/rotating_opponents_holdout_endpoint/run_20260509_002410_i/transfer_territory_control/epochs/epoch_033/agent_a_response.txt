def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    if not inside(sx, sy):
        sx, sy = 0, 0

    # Build a deterministic set of "frontier" unclaimed cells adjacent to opponent territory
    frontier = set()
    for x, y in opp_t:
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                frontier.add((nx, ny))

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    # Target selection
    if frontier:
        tx, ty = sorted(frontier, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))[0]
    else:
        edge_unclaimed = [c for c in (unclaimed or []) if (c[0] in (0, w-1) or c[1] in (0, h-1)) and c not in obstacles]
        if edge_unclaimed:
            tx, ty = sorted(edge_unclaimed, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))[0]
        elif resources:
            # resources are locations; head toward the closest valid one
            valid_res = [tuple(r) for r in resources if len(r) == 2 and inside(r[0], r[1]) and tuple(r) not in obstacles]
            if valid_res:
                tx, ty = sorted(valid_res, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))[0]
            else:
                tx, ty = sx, sy
        else:
            # If nothing else, push toward opponent territory roughly (centroid)
            if opp_t:
                xs = [p[0] for p in opp_t]; ys = [p[1] for p in opp_t]
                cx = sum(xs)//len(xs); cy = sum(ys)//len(ys)
                tx, ty = cx, cy
            else:
                tx, ty = sx, sy

    # Score candidate moves deterministically
    def cell_score(nx, ny):
        if (nx, ny) in obstacles or not inside(nx, ny):
            return -10**9
        # Great if capturing frontier (adjacent to opponent through unclaimed)
        if (nx, ny) in frontier:
            return 10000 - (abs(nx - sx) + abs(ny - sy))
        # Otherwise, prefer moving to unclaimed (still usually beneficial)
        if (nx, ny) in unclaimed:
            return 2000 - (abs(nx - sx) + abs(ny - sy))
        # Otherwise, reduce distance to target and opponent region
        d = abs(nx - tx) + abs(ny - ty)
        return 500 - d

    best = None
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < tuple(best_move)):
            best_score = sc
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]