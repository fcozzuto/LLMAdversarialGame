def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    turn = int(observation.get("turn_index", 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    k = turn % len(dirs)
    dirs = dirs[k:] + dirs[:k]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target: try center-ish unclaimed; if none, chase opponent territory; else go to any unclaimed
    cx, cy = (w - 1) // 2, (h - 1) // 2
    if unclaimed:
        ranked = sorted(unclaimed, key=lambda p: (dist(cx, cy, p[0], p[1]), p[0], p[1]))
        target = ranked[min(10, len(ranked)) - 1]
    else:
        opp_list = list(opp_terr)
        target = sorted(opp_list or [(cx, cy)], key=lambda p: (dist(ox, oy, p[0], p[1]), p[0], p[1]))[0]

    best = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        cell = (nx, ny)
        if cell in self_terr:
            own = 1
        else:
            own = 0
        if cell in opp_terr:
            opp = 1
        else:
            opp = 0
        un = 1 if cell not in self_terr and cell not in opp_terr else 0

        # Heuristic: move toward target, but value unclaimed highest; own next; opponent lowest (but can flip)
        to_t = dist(nx, ny, target[0], target[1])
        to_o = dist(nx, ny, ox, oy)
        capture_bonus = (30 if un else 8 if own else 4 if opp else 0)
        # Small pressure to reduce opponent mobility around their center-ish cells
        opp_pressure = -1 * (0 if (nx, ny) in opp_terr else dist(nx, ny, ox, oy) // 2)

        score = capture_bonus * 10_000 - to_t * 100 - to_o * 3 + opp_pressure + (dx == 0 and dy == 0) * -5
        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best = [dx, dy]

    return best