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
        if not valid(x0, y0):
            return [[INF] * h for _ in range(w)]
        dist = [[INF] * h for _ in range(w)]
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_score = -INF
    for rx, ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        # Win-race priority then shortest self arrival; deterministic tie-break to top-left
        score = (do - ds) * 1000 - ds * 2 - (rx * 0.01 + ry * 0.001)
        if score > best_score:
            best_score = score
            best = (rx, ry, ds)

    if best is None:
        return [0, 0]

    tx, ty, ds_target = best
    # Choose next step that greedily reduces distance to the target; tie-break toward target
    best_move = (0, 0)
    best_step = INF
    best_tieb = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # distance to target via BFS from current might be expensive; approximate by decreasing ds to target using distS
        # We can use distS to target by BFS from target, but we keep it light: use Chebyshev toward target as tiebreak,
        # and primary criterion is minimizing distS[nx][ny] + dist from (nx,ny) to target not available; fallback to ds' toward target.
        # Use heuristic: minimize distS[nx][ny] + cheb to target (safe and deterministic).
        ds_here = distS[nx][ny]
        cheb = abs(tx - nx); cd = cheb if cheb > abs(ty - ny) else abs(ty - ny)
        step_score = ds_here + cd
        tieb = abs(tx - nx) + abs(ty - ny)
        if step_score < best_step or (step_score == best_step and tieb < best_tieb):
            best_step = step_score
            best_tieb = tieb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]