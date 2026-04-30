def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        INF = 10**6
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not free(x0, y0):
            return dist
        qx = [x0]; qy = [y0]; qi = 0
        dist[x0][y0] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = -10**18

    def neighbor_pref(x, y):
        return -((x - cx) * (x - cx) + (y - cy) * (y - cy))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if not resources:
            score = neighbor_pref(nx, ny)
        else:
            mydist_next = myd[nx][ny]
            # If we can't reach, heavily penalize.
            if mydist_next >= 10**5:
                score = -10**12
            else:
                max_adv = -10**18
                for rx, ry in resources:
                    md = mydist_next
                    od = opd[rx][ry]
                    if od >= 10**5:
                        continue
                    adv = od - md
                    if adv > max_adv:
                        max_adv = adv
                # Encourage taking resources when we are at least as fast as opponent.
                # Also break ties by improving our own distance to the best target.
                if max_adv == -10**18:
                    score = neighbor_pref(nx, ny)
                else:
                    score = max_adv * 1000 - mydist_next + neighbor_pref(nx, ny) * 0.001
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]