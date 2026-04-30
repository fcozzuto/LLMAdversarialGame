def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-dir
    if not resources:
        # fallback: head to center
        tx, ty = (w-1)/2.0, (h-1)/2.0
        moves = [(dx, dy) for dx in (-1,0,1) for dy in (-1,0,1) if not (dx==0 and dy==0)] + [(0,0)]
        best = (10**9, 10**9, 10**9)
        bestm = (0,0)
        idx0 = observation.get("turn_index", 0) % len(moves)
        for k in range(len(moves)):
            m = moves[(idx0+k) % len(moves)]
            nx, ny = clamp(sx+m[0], sy+m[1])
            if (nx, ny) in obstacles: 
                continue
            score = (dist((nx,ny),(tx,ty)), abs((nx-ox))+abs((ny-oy)), m[0]*2+m[1])
            if score < best:
                best = score; bestm = m
        return [int(bestm[0]), int(bestm[1])]
    # choose a contested target: minimize (my_dist - opp_dist), prefer resources I can reach first
    ti = observation.get("turn_index", 0)
    candidates = []
    for rx, ry in resources:
        md = dist((sx,sy),(rx,ry))
        od = dist((ox,oy),(rx,ry))
        gap = md - od
        candidates.append((gap, md, od, rx, ry))
    candidates.sort(key=lambda t: (t[0], t[1], t[2], (t[3]+t[4]+ti) % 3))
    # pick among top few deterministically with parity to change strategy each epoch/turn
    topk = candidates[:min(4, len(candidates))]
    pick = topk[(ti // 2) % len(topk)]
    _, _, _, tx, ty = pick
    moves = [(dx, dy) for dx in (-1,0,1) for dy in (-1,0,1)]
    # deterministic move ordering starting point
    start = (ti % 9)
    best_score = (10**9, 10**9, 10**9, 10**9)
    best_move = (0,0)
    for k in range(9):
        dx, dy = moves[(start+k) % 9]
        nx, ny = clamp(sx+dx, sy+dy)
        if (nx, ny) in obstacles:
            continue
        my_d = dist((nx, ny), (tx, ty))
        # contest pressure: prefer moves that reduce opponent's distance to the same target less than mine (i.e., keep advantage)
        opp_d = dist((ox, oy), (tx, ty))
        # secondary: avoid stepping into squares that increase my distance to nearest resource (anti-stall)
        near_d = 10**9
        for rx, ry in resources:
            near_d = min(near_d, dist((nx,ny),(rx,ry)))
        score = (my_d, near_d, -((sx-nx)*(tx-sx)+(sy-ny)*(ty-sy)), (dx*2+dy))
        if score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]