def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
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
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    def best_target():
        best = None
        best_sc = -INF
        any_reach = False
        for rx, ry in resources:
            ds = distS[rx][ry]
            do = distO[rx][ry]
            if ds >= INF: 
                continue
            any_reach = True
            # Prefer resources we can beat; if none, race the closest.
            beat = do - ds
            sc = (beat * 10) - (ds * 1.0)
            if beat <= 0:
                sc = beat * 5 - ds * 2.0
            if sc > best_sc:
                best_sc = sc
                best = (rx, ry, ds, do)
        if best is None and any_reach:
            # Fallback: closest reachable
            best = None
            best_sc = INF
            for rx, ry in resources:
                ds = distS[rx][ry]
                if ds < INF and ds < best_sc:
                    best_sc = ds
                    best = (rx, ry, ds, distO[rx][ry])
        return best

    tgt = best_target()
    if tgt is None:
        return [0, 0]
    tx, ty, _, _ = tgt

    # If target is the current cell (should be terminal soon), stay.
    if sx == tx and sy == ty:
        return [0, 0]

    opp_dist_now = max(abs(sx - ox), abs(sy - oy))

    best_move = [0, 0]
    best_key = (-INF, -INF)  # (reduce distance, increase opponent distance)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_here = distS[nx][ny]
        ds_tgt = distS[tx][ty]
        # Key: minimize distance-to-target implicitly via distS from start:
        # pick move that gives smaller distS to tx,ty after one step by using triangle inequality:
        # Approx: minimize (distS[nx][ty]) if reachable.
        d_to = distS[nx][ty]
        if d_to >= INF:
            continue
        # Prefer closer to target; tie-break by maximizing distance from opponent
        opp_d = max(abs(nx - ox), abs(ny - oy))
        key = (-(d_to), opp_d)
        if key > best_key:
            best_key = key
            best_move = [dx, dy]

    # Extra deterministic correction: if all moves are invalid by dist, move that maximizes safety.
    if best_move == [0, 0]: