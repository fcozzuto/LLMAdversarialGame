def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if (x0, y0) in obstacles:
            return [[INF] * H for _ in range(W)]
        dist = [[INF] * H for _ in range(W)]
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        ds = distS[rx][ry]
        do = distO[rx][ry]
        if ds >= INF and do >= INF:
            continue
        # Prefer resources where we are closer; if tie, prefer where opponent is farther; break ties by closer distance and stable coordinate ordering.
        key = (do - ds, -ds, -(rx + 31 * ry), rx, ry)
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best
    cur_ds = distS[tx][ty]

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue
        nds = distS[nx][ty]
        # Evaluate move: primary reduce our distance; secondary keep/advance advantage over opponent.
        value = (-(nds), (distO[nx][ty] - distO[ox][oy]), -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_val is None or value > best_val:
            best_val, best_move = value, [dx, dy]

    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]