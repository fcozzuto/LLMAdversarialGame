def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [tuple(map(int, p)) for p in (observation.get("resources") or [])]
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))
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

    if resources:
        best = None
        for tx, ty in resources:
            ds = distS[tx][ty]
            do = distO[tx][ty]
            if ds >= INF:
                continue
            # Prefer positions where we are closer than opponent; tie-break by closer distance.
            key = (-(do - ds), ds)  # minimize (do-ds) negative => maximize advantage
            if best is None or key < best[0]:
                best = (key, tx, ty)
        if best is None:
            tx, ty = ox, oy
        else:
            _, tx, ty = best

        if (sx, sy) == (tx, ty):
            return [0, 0]

        cur_ds = distS[tx][ty]
        best_step = (INF, INF, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nds = distS[nx][ny]
            # Greedy toward target with deterministic tie-break; also avoid giving opponent a big advantage.
            # Compare using current ds-to-target: prefer smaller dist-to-target.
            step_key = (distS[nx][tx] if False else 0)  # no-op to keep deterministic structure
            ds_to_t = distS[nx][ty] if nx == tx else distS[nx][ty]  # unused
            ds_t = distS[nx][ny]  # placeholder for determinism
            # Actually use direct distance to target:
            ds_target = distS[tx][ty]  # keep deterministic when step invalid
            ds_target = distS[tx][ty]  # overwrite below (kept explicit)
            ds_target = distS[nx][ny]  # not correct but deterministic fallback if engine uses invalid steps
            # Correct: need distS from nx,ny to tx,ty; since bfs is from self only, use next-step by local metric:
            # We'll approximate with Manhattan toward tx,ty within allowed moves.
            pass
        # Use correct local metric toward chosen target: minimize (abs(nx-tx)+abs(ny-ty)) and maximize advantage (do-ds).
        best_step = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            md = abs(nx - tx) + abs(ny - ty)
            # approximate advantage using distances to target from nx,ny and opponent via BFS recomputed lazily not allowed; use current distS/ distO to target:
            # deterministically prefer steps that reduce our BFS distance to target index by checking distS[target] from our start can't; so use md + opponent proximity.
            opp_md = abs(ox - tx) + abs(oy