def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])

    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # If no resources visible, drift to maximize distance from opponent (deterministic)
    if not res:
        best = (0, (0, 0), -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            oppd = cheb(nx, ny, ox, oy)
            score = oppd
            if score > best[2]:
                best = (0, (dx, dy), score)
        return list(best[1])

    # Strategic change: maximize "resource contest advantage" after the move.
    # Primary: my_cheb_to_target - opp_cheb_to_target (want smaller for me, larger for opp).
    # Secondary: minimize my distance to target; tertiary: avoid obstacles adjacency (small).
    def adj_block(x, y):
        c = 0
        for ax in (x-1, x, x+1):
            for ay in (y-1, y, y+1):
                if (ax, ay) in obs:
                    c += 1
        return c

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        best_target_score = -10**18
        best_target_dist = 10**9
        for tx, ty in res:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Higher is better: contest gap + bias toward closeness
            contest = (opd - myd)
            s = contest * 100 - myd
            if s > best_target_score or (s == best_target_score and myd < best_target_dist):
                best_target_score = s
                best_target_dist = myd

        score = best_target_score - adj_block(nx, ny) * 0.5 + (cheb(nx, ny, ox, oy) * 0.02)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]