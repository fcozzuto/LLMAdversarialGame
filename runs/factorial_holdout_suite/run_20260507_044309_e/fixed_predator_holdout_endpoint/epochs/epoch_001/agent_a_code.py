def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    self_pos = observation["self_position"]; opp_pos = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(o) for o in observation["obstacles"])
    sx, sy = self_pos; ox, oy = opp_pos
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def bfs(start):
        sx, sy = start
        INF = 10**9
        dist = [[INF]*h for _ in range(w)]
        dist[sx][sy] = 0
        qx = [sx]; qy = [sy]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            d = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if dist[nx][ny] > d:
                        dist[nx][ny] = d
                        qx.append(nx); qy.append(ny)
        return dist
    dist_s = bfs((sx, sy))
    dist_o = bfs((ox, oy))
    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles: 
            continue
        ds = dist_s[rx][ry]; do = dist_o[rx][ry]
        if ds >= 10**9: 
            continue
        # Prefer resources we reach sooner; break ties deterministically.
        key = (ds - do, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        tx, ty = w//2, h//2
    else:
        tx, ty = best[1]
    # Choose step that minimizes distance to target while avoiding obstacles; deterministic tie-break.
    target_dist = dist_s[tx][ty]
    cur_dist = dist_s[sx][sy]
    best_step = (0,0)
    best_val = cur_dist
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles: 
            continue
        val = dist_s[nx][ny]
        if val < best_val or (val == best_val and (dx, dy) < best_step):
            best_val = val
            best_step = (dx, dy)
    if best_val >= 10**9:
        # Fallback: deterministic move towards center avoiding obstacles
        cx, cy = w//2, h//2
        pref = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                pref.append((abs(cx-nx)+abs(cy-ny), (dx, dy)))
        pref.sort()
        return list(pref[0][1]) if pref else [0,0]
    return [int(best_step[0]), int(best_step[1])]