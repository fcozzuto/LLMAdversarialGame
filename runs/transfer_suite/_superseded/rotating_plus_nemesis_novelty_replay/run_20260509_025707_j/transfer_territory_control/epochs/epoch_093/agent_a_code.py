def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set()
    obs_list = observation.get("obstacles") or []
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass
    res_list = observation.get("resources") or []
    resources = []
    for p in res_list:
        try:
            resources.append((p[0], p[1]))
        except:
            pass

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        if resources:
            d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            d_res = 0
        score = (-d_res, -d_opp, dx, dy)
        if best is None or score > best[0]:
            best = (score, [dx, dy])
    if best is not None:
        return best[1]
    return [0, 0]