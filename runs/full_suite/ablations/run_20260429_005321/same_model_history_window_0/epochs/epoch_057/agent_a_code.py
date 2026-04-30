def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((x, y) for x, y in obstacles)
    pos_set = obs_set  # for quick check
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-dir
    # If no resources, drift to center while avoiding obstacles
    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
        best = None; bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in pos_set: continue
            v = -dist((nx, ny), (tx, ty)) + (-(dist((nx, ny), (ox, oy)) < 2) * 0.5)
            if v > bestv: bestv = v; best = (dx, dy)
        return list(best if best else (0, 0))
    # Score a position by advantage over opponent toward each resource
    def score_pos(px, py):
        bestv = -10**9
        for rx, ry in resources:
            if (rx, ry) in pos_set: 
                continue
            md = dist((px, py), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Prefer closer to our position, farther from opponent; slightly favor picking any nearby resource
            v = (od - md) * 10.0 - md * 0.6
            # If we can grab quickly, boost
            if md <= 1: v += 30.0
            bestv = max(bestv, v)
        # Encourage not getting too close to opponent (tradeoff)
        bestv += max(0, dist((px, py), (ox, oy)) - 1) * 0.2
        return bestv
    best_move = (0, 0); best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not inb(nx, ny) or (nx, ny) in pos_set:
            continue
        v = score_pos(nx, ny)
        # If opponent is extremely close, prioritize running toward a target with maximal advantage
        if dist((sx, sy), (ox, oy)) <= 2:
            v += (dist((ox, oy), (nx, ny)) - dist((ox, oy), (sx, sy))) * 2.0
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]