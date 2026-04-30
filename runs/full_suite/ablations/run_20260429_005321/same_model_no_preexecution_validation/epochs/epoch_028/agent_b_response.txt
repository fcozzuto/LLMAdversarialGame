def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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
    if not resources or myd is None or opd is None:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    best = None  # (adv, -do, dm, rx, ry)
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        adv = (do - dm)  # positive means we get there first
        cand = (adv, -do, dm, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    _, _, _, tx, ty = best
    # If opponent is not slower, switch to a contest move that reduces their reach to the target.
    contest = (opd[ty][tx] - myd[ty][tx]) <= 0

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Objective favors shorter path for us to the target, and optionally longer for opponent when contesting.
        my_to_t = cheb(nx, ny, tx, ty)
        opp_to_t = cheb(ox, oy, tx, ty)
        val = -my_to_t
        if contest:
            # Make move that increases the gap immediately via target contest pressure.
            val += (opp_to_t - my_to_t) * 2
        else:
            # Otherwise greedily reduce our distance.
            val += (opd[ty][tx] - myd[ty][tx