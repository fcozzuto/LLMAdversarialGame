def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def bfs_dist(startx, starty):
        if (startx, starty) in obstacles or not inb(startx, starty):
            return None
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        dist[startx][starty] = 0
        qx, qy = [startx], [starty]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            dcur = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and dcur < dist[nx][ny]:
                    dist[nx][ny] = dcur
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dist_from_opp = bfs_dist(ox, oy)
    if dist_from_opp is None:
        return [0, 0]

    role = observation.get("self_role", "")
    we_are_evader = (role == "evader")

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist_from_opp[nx][ny]
        if d >= 10**9:
            continue
        # If evader: maximize distance; if pursuer: minimize distance.
        primary = d if we_are_evader else -d

        # Mobility + obstacle avoidance tie-breakers
        free = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obstacles:
                free += 1
        # Nudge toward corners for evader; toward center for pursuer
        corner_bias = (nx in (0, w - 1)) + (ny in (0, h - 1))
        center_bias = -((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2)
        tie = free + (corner_bias if we_are_evader else 0) + (0 if we_are_evader else 0.01 * center_bias)
        key = (primary * 1000 + tie)
        if best is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]