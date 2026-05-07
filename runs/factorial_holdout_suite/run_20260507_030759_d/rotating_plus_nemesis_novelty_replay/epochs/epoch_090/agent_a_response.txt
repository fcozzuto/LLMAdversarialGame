def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def bfs(start):
        dist = {}
        qx = [start[0]]
        qy = [start[1]]
        dist[(start[0], start[1])] = 0
        qi = 0
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            d = dist[(x, y)]
            qi += 1
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if (nx, ny) not in dist:
                        dist[(nx, ny)] = nd
                        qx.append(nx)
                        qy.append(ny)
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) not in ds:
            continue
        d1 = ds[(rx, ry)]
        d2 = do.get((rx, ry), 10**9)
        # Prefer winning races; then prefer faster arrival; then prefer resource far from opponent
        key = (d2 - d1, -(d1), d2 - (abs(rx - ox) + abs(ry - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best
    curd = ds.get((sx, sy), 0)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Move to neighbor that keeps shortest-path distance to target
    best_move = (0, 0)
    best_dist = 10**9
    # Compute distance-to-target by reusing BFS from target (small grid)
    dt = bfs((tx, ty))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) in dt:
            dd = dt[(nx, ny)]
            if dd < best_dist or (dd == best_dist and (dx, dy) < best_move):
                best_dist = dd
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]