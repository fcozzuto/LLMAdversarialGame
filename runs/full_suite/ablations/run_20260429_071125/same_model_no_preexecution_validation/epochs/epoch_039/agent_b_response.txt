def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_target = None
    best_val = -INF
    for rx, ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: continue
        # Favor earliest for us, latest for opponent; strongly prefer win on time.
        val = (do - ds) * 100 - ds
        if val > best_val or (val == best_val and (rx, ry) < best_target):
            best_val = val
            best_target = (rx, ry)

    # If no reachable resources, drift toward opponent side while avoiding obstacles.
    if best_target is None:
        tx, ty = (w - 1 if ox < w - 1 else ox, h - 1 if oy < h - 1 else oy)
    else:
        tx, ty = best_target

    # Choose move that minimizes our distance to target; break ties by maximizing opponent distance.
    best_move = (0, 0)
    best_score = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        ns = distS[nx][ny]  # may be INF but target will still work
        d_to_target = distS[tx][ty]  # constant; use step heuristics instead
        # Step quality: prefer moving closer (Chebyshev) to target, else toward opponent.
        closeness = -max(abs(tx - nx), abs(ty - ny))
        oppiness = distO[nx][ny] * 0.01
        # If best_target exists, also prefer closer path to it using distS from neighbor to target via BFS recompute not allowed.
        # Approximate by closeness + whether we can potentially beat opponent on target:
        if best_target is not None:
            beat = (distS[nx][ny] + distS[tx][ty] if distS[nx][ny] < INF and distS[tx][ty] < INF else INF)
            # beat proxy: smaller is better
            win_proxy = -beat * 1e-4
        else:
            win_proxy = 0
        score = closeness + oppiness + win_proxy
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]