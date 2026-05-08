def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, (observation.get("self_position") or [0, 0]))
    ox, oy = map(int, (observation.get("opponent_position") or [w - 1, h - 1]))
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    # pick a target that is far from opponent (prefer breaking away) and reachable-ish
    best = None
    bestv = -10**18
    for c in unclaimed[:80]:
        if not (isinstance(c, (list, tuple)) and len(c) >= 2):
            continue
        x, y = int(c[0]), int(c[1])
        if not inside(x, y) or (x, y) in obs:
            continue
        d1 = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        v = (d2 - d1)  # far from opponent, nearer to self
        # mild bias to edges to limit opponent access when they are sweepers
        v += 6 * min(x, y, w - 1 - x, h - 1 - y)
        if v > bestv:
            bestv = v
            best = (x, y)
    if best is None:
        best = ((w - 1) // 2, (h - 1) // 2)
    tx, ty = best

    # evaluate immediate moves with a deterministic local heuristic
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestscore = -10**18

    self_terr = set((tuple(map(int, p)) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2))
    opp_terr = set((tuple(map(int, p)) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        # prefer moving toward target, while not stepping into opponent territory unless it helps
        to_t = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        away_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        step_score = -to_t + 1.35 * away_opp

        if (nx, ny) in opp_terr:
            step_score += 35  # entering flips control (good for a territory battle)
        if (nx, ny) in self_terr:
            step_score += 6    # consolidating our territory
        # discourage oscillations: favor staying slightly consistent with prior inferred direction by comparing to target
        if dx == 0 and dy == 0:
            step_score -= 2

        # small obstacle-avoidance pressure by penalizing moves adjacent to obstacles
        adj_pen = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            px, py = nx + ax, ny + ay
            if (px, py) in obs:
                adj_pen += 1
        step_score -= 3 * adj_pen

        if step_score > bestscore:
            bestscore = step_score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]