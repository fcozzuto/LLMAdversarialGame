def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def md(a, b, x, y):
        return abs(a - x) + abs(b - y)

    # Precompute opponent boundary adjacency for scoring
    opp_adj = set()
    for (x, y) in opp_terr:
        for dx, dy in dirs[:-1]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                opp_adj.add((nx, ny))

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_terr:
            score += 1200
            score += -md(ox, oy, nx, ny)
            score += 5 if (nx, ny) in opp_adj else 0
        elif (nx, ny) in unclaimed:
            score += 300
            score += 120 if (nx, ny) in opp_adj else 0
            score += -md(ox, oy, nx, ny)
            score += 10 if (nx, ny) not in my_terr else 0
        elif (nx, ny) in my_terr:
            score += 30
            score += -md(ox, oy, nx, ny)
        else:
            score += 5
            score += -md(ox, oy, nx, ny)

        # Mild center preference to avoid getting stuck on edges
        cx, cy = w // 2, h // 2
        score += -0.5 * md(cx, cy, nx, ny)

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]