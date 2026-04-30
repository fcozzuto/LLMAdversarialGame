def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    # If no resources, run toward center while avoiding opponent a bit
    if not resources:
        tx, ty = (w - 1) / 2, (h - 1) / 2
        best = [0, 0, -10**9]
        for dx, dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                continue
            dcent = abs(nx - tx) + abs(ny - ty)
            dopp = abs(nx - ox) + abs(ny - oy)
            score = (dopp * 0.6) - dcent
            if score > best[2]:
                best = [dx, dy, score]
        return [best[0], best[1]]
    # Two-mode deterministic strategy: alternate focus to escape stagnation
    mode = (observation["turn_index"] // 4) % 2  # 0: contest resources, 1: prioritize blocking via distance pressure
    candidates = [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    # Choose target resource with objective based on our/opp distances
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    opp = (ox, oy)
    best_r = None
    best_val = None
    for r in resources:
        rv = (r[0], r[1])
        if rv in obstacles:
            continue
        ds = dist((sx, sy), rv)
        do = dist(opp, rv)
        if mode == 0:
            # contest: smallest (we-opp distance difference), then closest ours
            val = (ds - do, ds, do)
        else:
            # pressure: prefer resources where we are close and opponent is far
            val = (ds, -do, ds - do)
        if best_val is None or val < best_val:
            best_val = val
            best_r = rv
    tx, ty = best_r
    # Pick move that improves objective; also keep distance from opponent
    best = [0, 0, -10**9]
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        ds_new = abs(nx - tx) + abs(ny - ty)
        ds_cur = abs(sx - tx) + abs(sy - ty)
        dopp_new = abs(nx - ox) + abs(ny - oy)
        dopp_cur = abs(sx - ox) + abs(sy - oy)
        # Small directional preference to reduce distance; stronger if we can reduce by at least 1
        prog = ds_cur - ds_new
        score = prog * 10 + dopp_new * 0.8 + (1 if mode == 0 else 0) * (dopp_new - dopp_cur) * 0.2
        if score > best[2]:
            best = [dx, dy, score]
    return [best[0], best[1]]