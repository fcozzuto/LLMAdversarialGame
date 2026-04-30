def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    width, height = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(nx, ny):
        return 0 <= nx < width and 0 <= ny < height

    opp_dist = (x - ox) * (x - ox) + (y - oy) * (y - oy)
    best = None
    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            dmin = 10**18
            for rx, ry in resources:
                dd = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if dd < dmin:
                    dmin = dd
            # Contest bonus: prefer moves that keep being closer to resources than opponent (on avg)
            opp_dmin = 10**18
            for rx, ry in resources:
                dd = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
                if dd < opp_dmin:
                    opp_dmin = dd
            contest = (opp_dmin - dmin)
            # Repel opponent slightly to reduce their approach
            repel = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = (-dmin) + 0.002 * contest + 0.0005 * repel
        else:
            # No visible resources: drift toward center while not suiciding into opponent
            cx, cy = (width - 1) / 2.0, (height - 1) / 2.0
            center_d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            repel = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = (-center_d) + 0.001 * repel + 0.0001 * (repel - opp_dist)
        key = (score, -dx, -dy)  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is not None:
        return best[1]
    return [0, 0]