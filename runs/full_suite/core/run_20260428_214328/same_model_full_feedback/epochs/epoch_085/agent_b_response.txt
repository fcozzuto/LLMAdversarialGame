def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not valid(start[0], start[1]):
            return dist
        sx0, sy0 = start
        dist[sx0][sy0] = 0
        qx, qy = [sx0], [sy0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    my_dist_from = bfs_dist((sx, sy))
    op_dist_from = bfs_dist((ox, oy))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = my_dist_from[nx][ny]  # 0 for stay/varies, but we need distance-from-next
        next_dists = bfs_dist((nx, ny))
        val = -10**18
        if resources:
            for tx, ty in resources:
                myt = next_dists[tx][ty]
                if myt >= 10**8:
                    continue
                opt = op_dist_from[tx][ty]
                if opt >= 10**8:
                    opt = 10**8
                # Prefer resources where we are clearly closer, then shorter arrival.
                val = max(val, (opt - myt) * 1000 - myt)
        else:
            # No resources known: hold distance from opponent while not walking into walls.
            dcheb = max(abs(nx - ox), abs(ny - oy))
            val = dcheb * 10 - (abs(nx - (w - 1)) + abs(ny - (h - 1))) * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]