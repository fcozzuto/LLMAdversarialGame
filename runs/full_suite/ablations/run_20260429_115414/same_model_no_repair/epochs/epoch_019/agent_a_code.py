def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        qx = [x0]
        qy = [y0]
        dist[y0][x0] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_r = None
    best_key = None
    for rx, ry in resources:
        d1 = myd[ry][rx]
        if d1 >= 10**9:
            continue
        d2 = opd[ry][rx]
        # Maximize how much earlier I can get it, and break ties by preferring earlier pickups.
        key = (d2 - d1, -d1, -(abs(rx - sx) + abs(ry - sy)), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    cur_d = myd[sy][sx]
    best_move = (0, 0)
    best_next_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = myd[ny][nx]
        if nd >= 10**9:
            continue
        # Prefer strictly improving distance to target; otherwise minimize it.
        opp_adv = opd[ty][tx] - myd[ny][nx]  # opponent relative to target, approximated
        key = (-(nd), -abs(tx - nx) - abs(ty - ny), opp_adv, -abs(dx) - abs(dy))
        if best_next_key is None or key > best_next_key:
            best_next_key = key
            best_move = (dx, dy)

    if best_next_key is None:
        return [0, 0]
    return [best_move[0], best_move[1]]