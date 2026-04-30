def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        # fallback: go toward opponent to contest
        tx, ty = ox, oy
    else:
        # Choose resource that is good for us and bad for opponent (deterministic tie-break)
        best = None
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(oy - ry)
            # prefer resources we can reach sooner; also prefer denser/safer by slight obstacle distance
            obs_pen = 0
            for ax, ay in ((rx + 1, ry), (rx - 1, ry), (rx, ry + 1), (rx, ry - 1)):
                if (ax, ay) in obstacles:
                    obs_pen += 1
            val = (do - ds) * 1000 - ds - obs_pen * 50
            key = (val, -do, -ds, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    dx = 0
    dy = 0
    # Evaluate candidate moves
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # score: move toward target; if ties, avoid stepping into cells near obstacles
            dist = abs(tx - nx) + abs(ty - ny)
            near_obs = 0
            for ax, ay in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)):
                if (ax, ay) in obstacles:
                    near_obs += 1
            opp_dist = abs(tx - ox) + abs(ty - oy)
            candidates.append((( -dist - near_obs * 0.3, -abs(ox - nx) - abs(oy - ny) * 0.05, mx, my), (mx, my)))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda t: t[0])
    return [candidates[0][1][0], candidates[0][1][1]]