def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    INF = 10**9
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0): return dist
        dist[x0][y0] = 0
        qx, qy, i = [x0], [y0], 0
        while i < len(qx):
            x, y = qx[i], qy[i]; i += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    # Pick a materially different target: prioritize winning a race to a resource.
    best = None
    best_key = None
    if resources:
        for rx, ry in sorted(resources):
            md, od = myd[rx][ry], opd[rx][ry]
            if md >= INF and od >= INF:
                continue
            race = (od - md)  # positive means I arrive earlier
            key = (race < 0, -race, md, od, rx, ry)
            if best_key is None or key < best_key:
                best_key, best = key, (rx, ry)
    if best is None:
        best = (w // 2, h // 2)

    tx, ty = best
    # Choose move with deterministic tie-break and strong obstacle avoidance.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in sorted(dirs8):
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        adj_obs = 0
        for ax, ay in dirs4:
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) in obstacles:
                adj_obs += 1
        md = myd[nx][ny]
        d_t = myd[tx][ty]
        # Encourage moving closer to target, discourage getting stuck and obstacle adjacency,
        # and keep trying to beat opponent on the target if possible.
        t_md = myd[nx][ty] if inb(nx, ny) else INF
        o_t = opd[tx][ny] if inb(nx, ny) else INF
        score = 0
        score += -abs(t_md - (d_t - 1))  # prefer consistent approach
        score += -(t_md) * 2
        score += (o_t - t_md) * 1.5
        score += -adj_obs * 3
        score += -md * 0.01
        key = (-(score), nx - sx, ny - sy, md, dx, dy)
        if best_move == [0, 0] and best_score == -10**18:
            best_score = score; best_move = [dx, dy]
        elif score > best_score or (score == best_score and key < (-(best_score), best_move[0], best_move[1], 0, best_move[0], best_move[1])):
            best_score =