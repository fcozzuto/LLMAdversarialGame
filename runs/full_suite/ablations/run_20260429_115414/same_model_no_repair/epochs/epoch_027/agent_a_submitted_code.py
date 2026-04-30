def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return [[INF] * w for _ in range(h)]
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x = qx[qi]
            y = qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
            continue
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= INF:
            continue
        # Prefer winning the race to the resource; tie-break by closer to us, then lexicographic.
        key = (-(d2 - d1), d1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No reachable resources: move toward center/open cell with lowest opponent proximity.
        tx, ty = (w // 2, h // 2)
        open_cells = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # Prefer reducing distance to center, and keeping away from opponent.
                open_cells.append((abs(nx - tx) + abs(ny - ty) + 0.5 * (max(0, opd[ny][nx] if opd[ny][nx] < INF else 8)),
                                   nx, ny))
        if not open_cells:
            return [0, 0]
        open_cells.sort(key=lambda z: (z[0], z[1], z[2]))
        _, nx, ny = open_cells[0]
        return [nx - sx, ny - sy]

    tx, ty = best
    tdist = bfs((tx, ty))

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d_to_target = tdist[ny][nx]
            if d_to_target >= INF:
                continue
            # Encourage not letting opponent gain: prefer moves where our advantage to target improves.
            my_to = myd[ny][nx]
            op_to = opd[ny][nx]
            adv = (opd[ty][tx] -