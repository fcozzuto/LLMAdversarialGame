def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"] if tuple(p) not in obstacles]

    def bfs(stx, sty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if (stx, sty) in obstacles:
            return dist
        dist[stx][sty] = 0
        q = [(stx, sty)]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        if d < dist[nx][ny]:
                            dist[nx][ny] = d
                            q.append((nx, ny))
        return dist

    sd = bfs(sx, sy)
    od = bfs(ox, oy)

    # If we can't move anywhere due to obstacles, just stay.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Pick a resource that we can reach earlier (primary), else minimize our disadvantage.
    best = None
    for rx, ry in resources:
        ds, do = sd[rx][ry], od[rx][ry]
        if ds >= 10**9 and do >= 10**9:
            continue
        # Score key: prefer ds < do; then most negative (ds-do); then smaller ds; then closer to opponent (reduce their alternative)
        lead = ds - do
        key = (1 if ds >= do else 0, lead, ds, -do, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]

    tx, ty = best[1]

    # Choose move that improves our distance to target while preserving advantage; deterministic tie-break.
    cur_ds = sd[tx][ty]
    oxlead = od[tx][ty]
    best_move = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = sd[nx][ny]  # not distance-to-target; use dist-to-target for nx
        dt = sd[nx][ny]  # placeholder to avoid recompute; we'll compute actual dist to target from BFS grid by sd at target? can't.
        # Use known BFS distances from start: since BFS grid gives dist from (sx,sy) not from (nx,ny),
        # approximate by stepping direction toward target in BFS metric: compare dist-to-target from current position.
        # Instead, directly use cheb toward target for step ranking, while using BFS distances for lead check at target.
        cheb_step = max(abs((nx - tx)), abs((ny - ty)))
        # Lead after step approximated by comparing our current distance to target vs opponent's current to target:
        # choose step that minimizes cheb_step; tie-break by avoiding moves that increase cheb_step and by deterministic order.
        key = (cheb_step, -oxlead, dx, dy)
        if best_move[0] == 10**9 or key < best_move:
            best_move = key + (0, 0, 0, 0, 0)
    return [best_move[2], best_move[3]]