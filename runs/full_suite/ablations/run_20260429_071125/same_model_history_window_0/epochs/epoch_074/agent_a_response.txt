def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
        best = (10**9, 0, 0)
        for dx, dy in cand:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            d = abs(nx-tx) + abs(ny-ty)
            if d < best[0]: best = (d, dx, dy)
        return [best[1], best[2]] if best[0] < 10**9 else [0,0]
    best = (10**9, 0, 0)
    for dx, dy in cand:
        nx, ny = sx+dx, sy+dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate this move by the best resource we can contest.
        best_res_val = 10**9
        for rx, ry in resources:
            ds = abs(nx-rx) + abs(ny-ry)
            do = abs(ox-rx) + abs(oy-ry)
            # Favor resources closer to us than opponent.
            val = ds - 0.35 * do
            # Strongly favor immediate collection.
            if nx == rx and ny == ry: val -= 1000
            if val < best_res_val: best_res_val = val
        # Tie-break: avoid moving away too much from the top target.
        dist_to_opponent = abs(nx-ox) + abs(ny-oy)
        dist_now = abs(sx-nx) + abs(sy-ny)
        val = best_res_val + 0.01 * dist_now - 0.001 * dist_to_opponent
        if val < best[0]:
            best = (val, dx, dy)
    return [best[1], best[2]] if best[0] < 10**9 else [0,0]