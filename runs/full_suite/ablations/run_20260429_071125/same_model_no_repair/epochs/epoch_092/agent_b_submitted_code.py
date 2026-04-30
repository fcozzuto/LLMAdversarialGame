def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    if not inb(sx, sy):
        return [0, 0]
    qx, qy = [sx], [sy]
    dist[sx][sy] = 0
    qi = 0
    while qi < len(qx):
        x, y = qx[qi], qy[qi]
        qi += 1
        nd = dist[x][y] + 1
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and nd < dist[nx][ny]:
                dist[nx][ny] = nd
                qx.append(nx)
                qy.append(ny)

    best_t = None
    best_d = INF
    best_key = None
    for tx, ty in resources:
        d = dist[tx][ty]
        if d < best_d:
            best_d = d
            best_t = (tx, ty)
            best_key = (tx + ty, tx, ty)
        elif d == best_d:
            key = (tx + ty, tx, ty)
            if key < best_key:
                best_t = (tx, ty)
                best_key = key

    tx, ty = best_t
    if best_d == INF:
        # No path to any resource; just pick a safe move that maximizes distance to obstacles
        def safety_score(x, y):
            if (x, y) in obstacles:
                return -1
            md = 0
            for ox, oy in obstacles:
                v = abs(ox - x) + abs(oy - y)
                if v > md:
                    md = v
            return md
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                sc = safety_score(nx, ny)
                cand = (sc, -nx, -ny)
                if cand > best:
                    best = cand
                    bd = (dx, dy)
        return [bd[0], bd[1]]

    # Move one step along a shortest path to (tx, ty)
    best_step = (0, 0)
    best_val = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and dist[nx][ny] < INF:
            # Prefer decreasing dist to target, then tie-break deterministically
            val = dist[nx][ny] + max(abs(tx - nx), abs(ty - ny)) * 0.01
            if val < best_val - 1e-12:
                best_val = val
                best_step = (dx, dy)
            elif abs(val - best_val) <= 1e-12:
                if (dx, dy) < best_step:
                    best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]