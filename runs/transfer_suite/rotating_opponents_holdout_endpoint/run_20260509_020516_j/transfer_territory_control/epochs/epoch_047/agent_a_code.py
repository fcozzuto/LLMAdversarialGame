def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    unC = set((int(c[0]), int(c[1])) for c in unclaimed if c and len(c) >= 2)

    opp_terr_list = observation.get("opponent_territory") or []
    oppT = set((int(t[0]), int(t[1])) for t in opp_terr_list if t and len(t) >= 2)

    my_terr_list = observation.get("self_territory") or []
    myT = set((int(t[0]), int(t[1])) for t in my_terr_list if t and len(t) >= 2)

    cx, cy = (W - 1) // 2, (H - 1) // 2

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs:
            sc = -10**8
        elif not (0 <= nx < W and 0 <= ny < H):
            sc = -10**8
        else:
            # Prefer expansion and counter-claim while staying near center
            if (nx, ny) in oppT:
                sc = 300 - (abs(nx - ox) + abs(ny - oy))
            elif (nx, ny) in unC:
                sc = 220
            elif (nx, ny) in myT:
                sc = 160
            else:
                sc = 40

            # Avoid getting boxed: discourage adjacency to obstacles too heavily
            adj_obs = 0
            for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obs:
                    adj_obs += 1
            sc -= 15 * adj_obs

            # Slightly prefer moving toward center and toward expanding frontier
            sc += 5 * (8 - (abs(nx - cx) + abs(ny - cy)))
            # Frontier push: if adjacent to my territory, prefer
            frontier = 0
            for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                if (nx + ax, ny + ay) in myT:
                    frontier = 1
            sc += 18 * frontier

        if sc > best_score:
            best_score = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]