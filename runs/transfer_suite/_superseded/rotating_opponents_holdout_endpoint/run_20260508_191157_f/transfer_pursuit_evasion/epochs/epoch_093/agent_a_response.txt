def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_role = observation.get("self_role", "pursuer")
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cap = int(observation.get("capture_radius", 0))

    def bfs_dist(start, goal):
        if start == goal:
            return 0
        qx = [start[0]]
        qy = [start[1]]
        dist = [[None] * h for _ in range(w)]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obstacles:
                    continue
                if dist[nx][ny] is None:
                    dist[nx][ny] = nd
                    if nx == goal[0] and ny == goal[1]:
                        return nd
                    qx.append(nx)
                    qy.append(ny)
        return 10**9

    if self_role == "pursuer":
        best_move = None
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            if cap <= 0 and nx == ox and ny == oy:
                return [dx, dy]
            d = bfs_dist((nx, ny), (ox, oy))
            if d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d = d
                best_move = (dx, dy)
        if best_move is None:
            best_move = (0, 0)
        return [best_move[0], best_move[1]]

    # evader
    best_move = None
    best_score = -1
    base_dxdy = (1, 0)  # deterministic tie bias
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if cap <= 0 and nx == ox and ny == oy:
            continue
        d = bfs_dist((ox, oy), (nx, ny))
        score = d
        if score > best_score or (score == best_score and ((dx, dy) < best_move if best_move is not None else True)):
            best_score = score
            best_move = (dx, dy)
    if best_move is None:
        best_move = base_dxdy
        if not (0 <= sx + best_move[0] < w and 0 <= sy + best_move[1] < h) or (sx + best_move[0], sy + best_move[1]) in obstacles:
            best_move = (0, 0)
    return [best_move[0], best_move[1]]