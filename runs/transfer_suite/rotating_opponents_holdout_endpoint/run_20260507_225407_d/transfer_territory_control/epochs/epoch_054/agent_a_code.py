def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = (-10**9, dirs[0])
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        in_un = (nx, ny) in unclaimed
        in_opp = (nx, ny) in opp_terr
        adj_opp = abs(nx - ox) <= 1 and abs(ny - oy) <= 1
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = 0
        score += 300 if in_un else 0
        score += 120 if in_opp else 0
        score += 40 if adj_opp else 0
        score += -dist_opp
        if score > best[0]:
            best = (score, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]