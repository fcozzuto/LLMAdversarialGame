def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_terr = observation.get("opponent_territory") or []
    self_terr = set(tuple(map(int, p)) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(map(int, p)) for p in opp_terr)

    resources = [tuple(map(int, p)) for p in (observation.get("resources") or []) if isinstance(p, (list, tuple)) and len(p) == 2]
    unclaimed = [tuple(map(int, p)) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) == 2]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_frontier = []
    if opp_set:
        for (px, py) in opp_set:
            for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
                nx, ny = px + dx, py + dy
                if inside(nx, ny) and (nx, ny) not in opp_set and (nx, ny) not in obstacles:
                    opp_frontier.append((nx, ny))
    if not opp_frontier:
        opp_frontier = unclaimed if unclaimed else [(ox, oy)]

    targets = resources if resources else opp_frontier
    best = None
    bestv = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr:
            own_pen = 0.35
        else:
            own_pen = 0.0

        d_t = 10**9
        for tx, ty in targets:
            md = abs(nx - tx) + abs(ny - ty)
            if md < d_t:
                d_t = md

        d_opp = abs(nx - ox) + abs(ny - oy)
        new_cells_bonus = 0.0
        if (nx, ny) not in self_terr and (nx, ny) not in opp_set:
            new_cells_bonus = -0.25

        score = d_t + 0.12 * d_opp + own_pen + new_cells_bonus
        # Prefer breaking into opponent boundary: reduce score if near frontier
        if opp_frontier and opp_set:
            df = 10**9
            for fx, fy in opp_frontier:
                md = abs(nx - fx) + abs(ny - fy)
                if md < df:
                    df = md
            score += 0.6 * df

        if bestv is None or score < bestv:
            bestv = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best