def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources:
        if p and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs:
                res.append(t)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def md(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    cx, cy = (W - 1) // 2, (H - 1) // 2

    best_move = (0, 0)
    best_val = -10**18

    if res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            my_d = min(md((nx, ny), r) for r in res)
            opp_d = min(md((ox, oy), r) for r in res) if res else 10**9
            val = (opp_d - my_d) * 1000 - my_d
            if (nx, ny) == (ox, oy):
                val -= 10**6
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = -md((nx, ny), (cx, cy))
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    dx, dy = best_move
    return [dx, dy]