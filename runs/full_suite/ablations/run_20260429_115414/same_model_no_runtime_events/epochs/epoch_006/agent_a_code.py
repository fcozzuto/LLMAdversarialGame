def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(a, b):
        dx = a[0] - b[0]; dx = dx if dx >= 0 else -dx
        dy = a[1] - b[1]; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def bfs(start):
        # 8-connected shortest path length avoiding obstacles
        dist = {(start[0], start[1]): 0}
        q = [start]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d0 = dist[(x, y)]
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not ok(nx, ny): 
                    continue
                nd = d0 + 1
                if (nx, ny) not in dist or nd < dist[(nx, ny)]:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return dist

    sd = bfs((sx, sy))
    od = bfs((ox, oy))

    INF = 10**9
    best = None
    best_key = None
    for rx, ry in resources:
        if not ok(rx, ry):
            continue
        md = sd.get((rx, ry), INF)
        odist = od.get((rx, ry), INF)
        if md >= INF and odist >= INF:
            continue
        # Prefer resources we can reach and where we minimize (md - odist)
        key = (md - odist, md, odist, cheb((sx, sy), (rx, ry)) - cheb((ox, oy), (rx, ry)), (rx * 7 + ry) % 1000)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else resources[0]

    def best_step(pos, target):
        px, py = pos
        bestd = None
        bestmv = (0, 0)
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny):
                continue
            t = cheb((nx, ny), target)
            mv = (dx, dy)
            if bestd is None or t < bestd or (t == bestd and mv < bestmv):
                bestd = t
                bestmv = mv
        return bestmv

    best_move = (0, 0)
    best_eval = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        omv = best_step((ox, oy), (tx, ty))
        nox, noy = ox + omv[0], oy + omv[1]
        md = sd.get((nx, ny), cheb((nx, ny), (tx, ty)))
        odist = od.get((nox, noy), cheb((nox, noy), (tx, ty)))
        # Maximize lead: smaller (md - odist) is better; tie-break closer to target and lexicographic move
        ev = (md - odist, md, odist, dx, dy)
        if best_eval is None or ev < best_eval:
            best_eval = ev
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]