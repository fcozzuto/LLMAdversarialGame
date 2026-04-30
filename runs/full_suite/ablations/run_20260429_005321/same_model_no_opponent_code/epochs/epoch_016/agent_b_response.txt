def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def cd2(ax, ay, bx, by):
        dx, dy = abs(ax - bx), abs(ay - by)
        return max(dx, dy)  # Chebyshev
    def near_obst_score(nx, ny):
        s = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            if (nx+dx, ny+dy) in obst: s += 2
        if (nx, ny) in obst: s += 100
        return s

    # If no resources, move toward center-ish away from obstacles; also slightly away from opponent.
    if not resources:
        cx, cy = (w-1)/2.0, (h-1)/2.0
        best = None
        for dx, dy in moves:
            nx, ny = x+dx, y+dy
            if not inside(nx, ny): continue
            score = -cd2(nx, ny, ox, oy) - near_obst_score(nx, ny) - cd2(nx, ny, int(round(cx)), int(round(cy))) * 0.2
            if best is None or score > best[0]: best = (score, dx, dy)
        return [best[1], best[2]]

    # Pick a deterministic "best contested resource": prioritize where we beat opponent and can get there quickly.
    # If we can't win any, shift to resources where opponent is farthest from.
    best_res = None
    for rx, ry in resources:
        ds = cd2(x, y, rx, ry)
        do = cd2(ox, oy, rx, ry)
        # Strongly prefer states where we can arrive no later than opponent.
        win_margin = do - ds
        score = win_margin * 120 - ds * 2 - (rx + ry) * 0.01
        if best_res is None or score > best_res[0]: best_res = (score, rx, ry)

    _, tx, ty = best_res

    # Evaluate immediate moves: chase target, avoid obstacles, and don't walk into opponent's immediate reach to contested tile.
    best_move = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = x+dx, y+dy
        if not inside(nx, ny): continue
        if (nx, ny) in obst: continue
        ds_next = cd2(nx, ny, tx, ty)
        do_next = cd2(ox, oy, tx, ty)
        # If opponent can arrive earlier/equal after our move, penalize.
        contest_pen = 90 if do_next <= ds_next else 0
        # If opponent is too close to us, lightly avoid.
        sep_pen = 18 if cd2(nx, ny, ox, oy) <= 1 else 0
        # Prefer moving toward target and slightly toward reducing opponent distance to *different* resources by generalization:
        toward = -ds_next * 3 - (abs(nx-tx)+abs(ny-ty))*0.03
        obstacle_pen = near_obst_score(nx, ny)
        score = toward - contest_pen - sep_pen - obstacle_pen
        if score > best_move[0]: best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]