def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    my_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []) if inside(int(x), int(y)))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []) if inside(int(x), int(y)))
    un_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []) if inside(int(x), int(y)))

    def neigh8_adj_to_my(x, y):
        for dx, dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in my_set:
                return True
        return False

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    center_targets = []
    for (tx, ty) in list(un_set)[:64]:
        center_targets.append((abs(tx - cx) + abs(ty - cy), tx, ty))
    if not center_targets:
        for (tx, ty) in list(opp_set)[:64]:
            center_targets.append((abs(tx - cx) + abs(ty - cy), tx, ty))
    center_targets.sort()
    tx, ty = (center_targets[0][1], center_targets[0][2]) if center_targets else (int(round(cx)), int(round(cy)))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            val = -10**9 - (abs(dx) + abs(dy)) * 10
        else:
            val = 0
            if (nx, ny) in opp_set:
                val += 500  # flipping opponent territory on entry
                val += 80 / (1 + (abs(nx - ox) + abs(ny - oy)))
            elif (nx, ny) in un_set:
                val += 220
                if neigh8_adj_to_my(nx, ny):
                    val += 90
            elif (nx, ny) in my_set:
                val += 20
            # steer towards center / frontier while keeping pressure
            val += 60 / (1 + (abs(nx - tx) + abs(ny - ty)))
            val += 15 / (1 + (abs(nx - ox) + abs(ny - oy)))
            # if we have a tiny territory, prioritize adjacency growth
            if len(my_set) < 6 and (nx, ny) in un_set and neigh8_adj_to_my(nx, ny):
                val += 60
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]