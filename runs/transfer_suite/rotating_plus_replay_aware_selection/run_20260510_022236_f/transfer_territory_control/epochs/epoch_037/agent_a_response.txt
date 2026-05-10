def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h and (x, y) not in obs
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        # Chase opponent boundary cells to flip control; otherwise drift to center/edge
        boundary = set()
        for ox, oy in opp_terr:
            for dx, dy in dirs:
                nx, ny = ox + dx, oy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and (nx, ny) not in opp_terr:
                    boundary.add((nx, ny))
        if boundary:
            tx, ty = min(boundary, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
        else:
            tx, ty = w // 2, h // 2

    best = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)

        # Prefer entering unclaimed/own to expand, and prefer opponent cells when flipping is possible.
        if (nx, ny) in unclaimed:
            cell_rank = 0
        elif (nx, ny) in my_terr:
            cell_rank = 1
        elif (nx, ny) in opp_terr:
            cell_rank = 2
        else:
            cell_rank = 3

        # Encourage moves that go toward our current territory mass if we are stuck.
        if my_terr:
            near_my = min(abs(mx - nx) + abs(my - ny) for mx, my in my_terr)
        else:
            near_my = 0

        cand = (dist, cell_rank, -near_my, dx, dy)
        if cand < best:
            best = cand

    return [int(best[3]), int(best[4])]