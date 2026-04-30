def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if resources:
        best = None; best_adv = None
        for r in resources:
            sd = dist((sx, sy), r); od = dist((ox, oy), r)
            adv = od - sd
            if best is None or adv > best_adv or (adv == best_adv and (r[0], r[1]) < best):
                best = (r[0], r[1]); best_adv = adv
        tx, ty = best
        def score_move(dx, dy):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: return -10**9
            self_d = dist((nx, ny), (tx, ty))
            opp_d = dist((nx, ny), (ox, oy))
            return (1000 - self_d) + (opp_d // 2)
        best_mv = None; best_sc = None
        for dx, dy in moves:
            sc = score_move(dx, dy)
            if best_mv is None or sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
                best_mv = (dx, dy); best_sc = sc
        return [best_mv[0], best_mv[1]]
    # No visible resources: move toward center while keeping away from opponent
    cx, cy = (w-1)//2, (h-1)//2
    best_mv = (0, 0); best_sc = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue
        sc = -(dist((nx, ny), (cx, cy))) + (dist((nx, ny), (ox, oy)) // 2)
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
            best_sc = sc; best_mv = (dx, dy)
    return [best_mv[0], best_mv[1]]