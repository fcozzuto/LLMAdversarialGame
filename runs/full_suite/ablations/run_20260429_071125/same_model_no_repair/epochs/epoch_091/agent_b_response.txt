def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(stx, sty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not (0 <= stx < w and 0 <= sty < h) or (stx, sty) in obstacles:
            return dist
        dist[stx][sty] = 0
        q = [(stx, sty)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    ds = bfs(sx, sy)
    do = bfs(ox, oy)

    best = None
    best_key = None
    for rx, ry in resources:
        a = ds[rx][ry]
        b = do[rx][ry]
        if a >= 10**9:
            continue
        # Prefer resources we can reach soon and that are relatively harder for opponent
        key = (a - (0.6 * b), a, -b, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    if best is None:
        return [0, 0]

    tx, ty = best
    dcur = ds[sx][sy]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dn = ds[nx][ny]
        if dn >= 10**9:
            continue
        if dn <= dcur:  # do not wander away from target
            dist_opp_next = do[nx][ny]
            candidates.append((dn, -dist_opp_next, abs(tx - nx) + abs(ty - ny), dx, dy))
    if candidates:
        candidates.sort()
        return [int(candidates[0][3]), int(candidates[0][4])]

    # Fallback: step that most reduces distance-to-target even if it temporarily increases ds
    best_step = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dn = ds[nx][ny]
        if dn >= 10**9:
            continue
        val = (dn, abs(tx - nx) + abs(ty - ny), -do[nx][ny], dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_step = [int(dx), int(dy)]
    return best_step