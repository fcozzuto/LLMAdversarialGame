def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    best_r = None
    best_key = None
    for rx, ry in resources:
        md = myd[rx][ry]; od = opd[rx][ry]
        if md >= INF and od >= INF:
            continue
        key = (od - md, -md, -abs(rx - ox) - abs(ry - oy), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        # Fallback: move to improve distance to opponent and avoid obstacles
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r

    # Greedy one-step toward target using BFS distances; tie-break deterministically
    curd = myd[sx][sy]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist_to_target = myd[nx][ny]
        # If BFS couldn't reach nx, discourage heavily
        score = (-(0 if dist_to_target >= INF else dist_to_target), -abs(nx - tx) - abs(ny - ty), dx, dy)
        candidates.append(score)
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    # Recompute best move from sorted scores
    best = candidates[0]
    # Map score's dx/dy back
    # Since score stores (a,b,dx,dy), extract dx,dy from last two elements
    dx, dy = int(best[2]), int(best[3])
    return [dx, dy]