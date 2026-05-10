def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    unclaimed = observation.get("unclaimed_cells") or []
    unset = set()
    for p in unclaimed:
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                    unset.add((x, y))
            except:
                pass

    frontier = []
    terr = observation.get("self_territory") or []
    if terr:
        terrset = set()
        for p in terr:
            if p and len(p) >= 2:
                try:
                    x, y = int(p[0]), int(p[1])
                    terrset.add((x, y))
                except:
                    pass
        for (x, y) in list(terrset):
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unset:
                    frontier.append((nx, ny))

    candidates = frontier if frontier else list(unset)
    if not candidates:
        # fallback: move toward center while avoiding obstacles
        tx, ty = w // 2, h // 2
    else:
        # deterministic scoring: prioritize nearest frontier/unclaimed; keep away from opponent a bit
        best = None
        bestv = 10**18
        for x, y in candidates:
            dv = abs(x - sx) + abs(y - sy)
            opp = abs(x - ox) + abs(y - oy)
            # prefer cells closer to us but farther from opponent; slight bias to bottom-right vs top-left by parity
            v = dv - 0.15 * opp + 0.01 * ((x + y) & 1)
            if v < bestv:
                bestv = v
                best = (x, y)
        tx, ty = best

    # choose among legal one-step moves the one that gets closer to target
    best_move = (0, 0)
    best_d = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        # discourage stepping onto opponent proximity (more stable vs sweeper)
        d2 = d + 0.02 * abs(nx - ox) + 0.02 * abs(ny - oy)
        if d2 < best_d:
            best_d = d2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]