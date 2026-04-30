def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]; i += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distO = bfs(ox, oy)

    def key_for_resource(r):
        rx, ry = r
        dO = distO[rx][ry]
        if dO >= INF: return (0, -INF)
        return (1, -dO)

    resources_sorted = sorted(resources, key=key_for_resource, reverse=True)

    best_move = (0, 0)
    best_tuple = (-10**18, -10**18, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        distN = bfs(nx, ny)
        win_count = 0
        sum_adv = 0
        best_adv = -10**18
        for rx, ry in resources_sorted:
            dS = distN[rx][ry]
            dO = distO[rx][ry]
            if dS >= INF or dO >= INF:
                continue
            adv = dO - dS
            if adv > 0:
                win_count += 1
                sum_adv += adv
                if adv > best_adv: best_adv = adv
        # Tie-break: prefer immediate closeness if no guaranteed wins
        if win_count == 0:
            closeness = -min((distN[rx][ry] for rx, ry in resources if valid(rx, ry) and distN[rx][ry] < INF), default=INF)
            tie = (win_count, sum_adv, best_adv, closeness)
            cur_tuple = (win_count, sum_adv, closeness)
        else:
            cur_tuple = (win_count, sum_adv, best_adv)
        if cur_tuple > best_tuple:
            best_tuple = cur_tuple
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]