def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0]); ox, oy = observation.get("opponent_position", [0, 0])
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    role = str(observation.get("self_role", "")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def bfs_from(start):
        x0, y0 = start
        dist = [[10**9] * h for _ in range(w)]
        if not inside(x0, y0):
            return dist
        qx = [x0]; qy = [y0]; dist[x0][y0] = 0
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]; head += 1
            d = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and dist[nx][ny] == 10**9:
                    dist[nx][ny] = d
                    qx.append(nx); qy.append(ny)
        return dist

    dist_self = bfs_from((sx, sy))
    dist_opp = bfs_from((ox, oy))

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if nx == ox and ny == oy:
            score = (1, 0, 0)  # immediate capture
        else:
            d_to_opp = dist_self[nx][ny]  # from self to candidate? dist_self is from self start, so use dist_self at candidate
            d_opp_to = dist_opp[nx][ny]   # from opponent to candidate
            if is_evader:
                # maximize distance (prefer unreachable over long distance), also avoid getting cornered
                score = (0, -d_opp_to, -(abs(nx - (w - 1 if (ox < w//2) else 0)) + abs(ny - (h - 1 if (oy < h//2) else 0))))
            else:
                # pursuer: minimize distance; tie-break by maximizing escape distance after move
                score = (0, d_to_opp, -d_opp_to)
        cand = (score, dx, dy)
        if best is None or cand < best:
            best = cand

    return [best[1], best[2]]