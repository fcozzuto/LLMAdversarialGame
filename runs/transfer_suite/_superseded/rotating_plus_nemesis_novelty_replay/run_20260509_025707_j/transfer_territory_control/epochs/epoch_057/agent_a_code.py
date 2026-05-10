def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_set = {(p[0], p[1]) for p in self_terr}
    opp_set = {(p[0], p[1]) for p in opp_terr}
    un_set = {(p[0], p[1]) for p in unclaimed}

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def adj_to_set(x, y, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in s:
                        return True
        return False

    best = None
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = 0
        if (nx, ny) in un_set:
            sc += 30
            if adj_to_set(nx, ny, opp_set):
                sc += 120
        if (nx, ny) in self_set:
            sc += 5
        if adj_to_set(nx, ny, opp_set):
            sc += 20
        if (nx, ny) in opp_set:
            sc -= 200
        sc -= abs(nx - ox) + abs(ny - oy)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        sc -= 0.1 * (abs(nx - cx) + abs(ny - cy))
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]