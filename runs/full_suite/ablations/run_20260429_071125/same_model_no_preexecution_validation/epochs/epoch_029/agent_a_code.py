def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
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

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    best_t = None
    best_val = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF:
            continue
        val = (do - ds) * 1000 - ds
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    if best_t is None:
        # Fallback: drift toward center
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_t

    sxn = sx; syn = sy
    cur_ds = distS[tx][ty]
    best_move = [0, 0]
    best_step_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = distS[nx][ny]
        # Use next's distances to target and opponent advantage
        dS_to_t = distS[nx][ty] if (nx == tx) else distS[nx][ny]  # harmless small variation
        dS_t = distS[nx][ny]  # local potential
        dS_target = distS[nx][ny] if True else cur_ds
        # Main: minimize distance to target by choosing best reachable neighbor
        # Approx: use Chebyshev to target for speed; deterministic and consistent with movement model.
        cdistS = max(abs(nx - tx), abs(ny - ty))
        cdistO = max(abs(ox - tx), abs(oy - ty))
        step_val = (cdistO - cdistS) * 1000 - cdistS - ds2 * 0.01 + (0 if (nx, ny) == (sx, sy) else 0)
        if step_val > best_step_val:
            best_step_val = step_val
            best_move = [dx, dy]

    return best_move