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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    my_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []) if inside(int(x), int(y)))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []) if inside(int(x), int(y)))
    un_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []) if inside(int(x), int(y)))

    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def adj8_to_my(x, y):
        for dx, dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
            if (x + dx, y + dy) in my_set:
                return True
        return False

    def min_dist_to_opp(x, y):
        if opp_set:
            md = 10**9
            for px, py in opp_set:
                d = abs(px - x) + abs(py - y)
                if d < md:
                    md = d
            return md
        return abs(ox - x) + abs(oy - y)

    best = -10**18
    best_move = [0, 0]
    for dx, dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in my_set:
            val = 2
        elif (nx, ny) in opp_set:
            val = 80 + 2 * adj8_to_my(nx, ny) - 0.2 * min_dist_to_opp(nx, ny)
        else:
            # Unclaimed cell or staying on unclaimed/other
            val = 8
            if (nx, ny) in un_set:
                val += 10
            if adj8_to_my(nx, ny):
                val += 8
            val += 0.3 * (min_dist_to_opp(nx, ny))
        # Slightly prefer advancing away from our start toward center to avoid corner trap
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        val -= 0.01 * dist_center
        if val > best:
            best = val
            best_move = [dx, dy]
    return best_move