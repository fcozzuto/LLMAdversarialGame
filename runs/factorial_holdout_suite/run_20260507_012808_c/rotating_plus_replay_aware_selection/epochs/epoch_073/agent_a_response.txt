def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    def greedy_step(px, py, opp_hint=False):
        best = None
        best_key = (10**18, 10**18, 0)
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            cell = (nx, ny)
            if cell in rset:
                key = (-1, 0, 0)
            else:
                best_dist = min(d(cell, rr) for rr in resources) if resources else 0
                key = (best_dist, -((nx + 31*ny) & 1023), 0)
            if key < best_key:
                best_key = key
                best = (dx, dy)
        return best if best is not None else (0, 0)

    rset = set(tuple(r) for r in resources)
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    opp_next = greedy_step(ox, oy, True)
    nox, noy = ox + opp_next[0], oy + opp_next[1]

    best_move = (0, 0)
    best_val = -10**18

    for mdx, mdy in dirs:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        cell = (nx, ny)
        score_self = 0
        score_opp = 0
        for rr in rset:
            if cell == rr:
                score_self += 1
                continue
            sd = d(cell, rr)
            od = d((nox, noy), rr)
            if sd <= od:
                score_self += 1
            else:
                score_opp += 1
        # Prefer immediate collection strongly, then higher net coverage, then move deterministically
        key = (score_self - score_opp, score_self, -((nx + 31*ny) & 1023))
        if key > (best_val, 0, -10**18):
            best_val = key[0]
            best_move = (mdx, mdy)

    return [best_move[0], best_move[1]]