def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass
    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_set = set()
    for r in resources:
        try:
            x, y = r
            res_set.add((x, y))
        except:
            pass

    if not res_set:
        # Drift to nearest corner-ish cell while avoiding obstacles
        prefs = [(w - 1, h - 1), (0, h - 1), (w - 1, 0), 0, 0]
        # Flatten deterministic: use two corners based on start
        cx, cy = (w - 1, h - 1) if (sx + sy) <= (w + h - 2 - (sx + sy)) else (0, 0)
        if (sx == cx and sy == cy) and inb(sx, sy):
            cx, cy = 0, h - 1
        best = (-10**18, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = abs(nx - cx) + abs(ny - cy)
                sc = -d
                if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    # Pick best resource target by advantage to collect before opponent
    best_res = None
    best_key = None
    for (rx, ry) in res_set:
        sd = abs(rx - sx) + abs(ry - sy)
        if opp_exists:
            od = abs(rx - ox) + abs(ry - oy)
            key = (-(od - sd), sd, rx, ry)  # minimize opponent advantage, then self distance
        else:
            key = (sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    # Evaluate one-step moves using obstacle check and immediate resource bonus
    best = (-10**18, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            immediate = 1 if (nx, ny) in res_set else 0
            sd = abs(tx - nx) + abs(ty - ny)
            if opp_exists:
                od = abs(tx - ox) + abs(ty - oy)
                # Encourage reducing gap to target vs opponent and grabbing now if possible
                sc = immediate * 10 + (od - sd)
            else:
                sc = immediate * 10 - sd
            if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
                best = (sc, dx, dy)
    return [best[1], best[2]]