def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not unclaimed:
        best = (0, 0)
        best_s = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d_op = abs(nx - ox) + abs(ny - oy)
            s = d_op + (1 if (nx, ny) in self_t else 0) - (3 if (nx, ny) in opp_t else 0)
            if s > best_s:
                best_s = s
                best = (dx, dy)
        return [best[0], best[1]]

    nearest_uc = {}
    for tx, ty in unclaimed:
        d = abs(tx - sx) + abs(ty - sy)
        if len(nearest_uc) < 12:
            nearest_uc[(tx, ty)] = d
        else:
            # keep small set of close targets
            max_k = max(nearest_uc, key=nearest_uc.get)
            if d < nearest_uc[max_k]:
                del nearest_uc[max_k]
                nearest_uc[(tx, ty)] = d
    targets = list(nearest_uc.keys()) or unclaimed[:12]

    best = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        in_uc = 1 if (nx, ny) in unclaimed else 0
        s = 0
        s += 60 if in_uc else 0
        s += 8 if (nx, ny) in self_t else 0
        s -= 70 if (nx, ny) in opp_t else 0
        s += d_opp * 0.5  # stay away from opponent
        # chase a nearby unclaimed cell
        md = 10**9
        for tx, ty in targets:
            dd = abs(nx - tx) + abs(ny - ty)
            if dd < md:
                md = dd
        s += -md
        if s > best_s:
            best_s = s
            best = (dx, dy)
    return [best[0], best[1]]