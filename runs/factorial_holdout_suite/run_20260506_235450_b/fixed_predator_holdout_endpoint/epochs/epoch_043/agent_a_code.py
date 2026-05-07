def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def bfs_from(start):
        sx0, sy0 = start
        dist = {(sx0, sy0): 0}
        q = [(sx0, sy0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[(x, y)]
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not in_bounds(nx, ny) or (nx, ny) in obstacles: 
                    continue
                if (nx, ny) not in dist:
                    dist[(nx, ny)] = d + 1
                    q.append((nx, ny))
        return dist

    self_dist = bfs_from((sx, sy))
    opp_dist = bfs_from((ox, oy))

    # Pick resource we can reach sooner with maximum "denial" margin.
    best = None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = self_dist.get((rx, ry), 10**9)
        od = opp_dist.get((rx, ry), 10**9)
        if sd >= 10**8 and od >= 10**8:
            continue
        key = (od - sd, -sd)  # maximize margin; then prefer shorter self distance
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    # Move one step that leads to minimal self distance-to-target.
    # Compute target-based distances by BFS from target (small grid).
    target_dist = bfs_from((tx, ty))
    best_step = (0, 0)
    best_d = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = target_dist.get((nx, ny), 10**9)
        if d < best_d or (d == best_d and (dx, dy) < best_step):
            best_d = d
            best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]