def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles if p is not None and len(p) >= 2}
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inside(x, y) and (x, y) not in obs
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    INF = 10**9
    def bfs_dist_from(x0, y0, xg, yg):
        if x0 == xg and y0 == yg: return 0
        if not legal(x0, y0): return INF
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not legal(nx, ny): 
                    continue
                if nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    if nx == xg and ny == yg:
                        return nd
                    qx.append(nx); qy.append(ny)
        return INF

    best = None
    best_key = None
    cur_m = abs(ox - sx) + abs(oy - sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = bfs_dist_from(nx, ny, ox, oy)
        nm = abs(ox - nx) + abs(oy - ny)
        key = (d, nm, -max(0, cur_m - nm), abs(dx) + abs(dy))
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    return best if best is not None else [0, 0]