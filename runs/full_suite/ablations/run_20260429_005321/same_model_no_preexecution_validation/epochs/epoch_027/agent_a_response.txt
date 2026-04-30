def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    best = None  # (adv, -do, dm, rx, ry)
    if resources and myd is not None and opd is not None:
        for rx, ry in resources:
            dm, do = myd[ry][rx], opd[ry][rx]
            if dm >= INF:
                continue
            # prioritize resources we can reach and opponent slower; also prefer quick targets
            adv = do - dm if do < INF else 10**6
            cand = (adv, -(do if do < INF else 0), dm, rx, ry)
            if best is None or cand > best:
                best = cand

    if best is None:
        # fallback: move toward center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        def score_step(nx, ny):
            md = abs(tx - nx) + abs(ty - ny)
            od = abs(ox - nx) + abs(oy - ny)
            return (-(md), od)
        bestm = (-(INF), None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                sc = score_step(nx, ny)
                if sc > bestm:
                    bestm = (sc, [dx, dy])
        return bestm[1] if bestm[1] is not None else [0, 0]

    _, _, _, rx, ry = best
    # choose a step that improves our distance to the chosen resource; if tied, hinder opponent
    cur_dm = myd[sy][sx]
    cur_do = opd[sy][sx] if opd is not None else INF
    best_step = (-(INF), None)  # (primary, -new_do, -new_dm, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ndm = myd[ny][nx] if myd is not None else INF
        if ndm >= INF:
            continue
        ndist_improve = cur_dm - ndm
        new_do = opd[ny][nx] if opd is not None else INF
        # primary: maximize improvement; secondary: maximize opponent distance (i.e., make it harder for them)
        cand = (ndist_improve, -(new_do if new_do < INF else 10**6), -(ndm), dx, dy)
        if best_step[0] < cand:
            best_step = (cand, [dx, dy])

    # ensure not to stay still if any improvement move exists
    if best_step[1] is not None and best_step[1] != [0, 0]:
        return best_step[1]
    if best_step[1] is not None:
        return best_step[1]
    return [0, 0]