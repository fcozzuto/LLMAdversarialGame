def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestc = None
        bestv = None
        for c in corners:
            v = md((sx, sy), c) - md((ox, oy), c)
            if bestv is None or v > bestv:
                bestv, bestc = v, c
        tx, ty = bestc
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for cand in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + cand[0], sy + cand[1]
            if inb(nx, ny):
                return [cand[0], cand[1]]
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_score = None

    res_set = set((int(r[0]), int(r[1])) for r in resources if r and len(r) >= 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        new_pos = (nx, ny)
        self_best = None
        opp_best = None
        for r in res_set:
            sd = md(new_pos, r)
            od = md((ox, oy), r)
            if self_best is None or sd < self_best:
                self_best = sd
            if opp_best is None or od < opp_best:
                opp_best = od
        # race advantage: lower is better for us
        race = (self_best - opp_best) if (self_best is not None and opp_best is not None) else 10**9
        # capture preference
        capture = 1 if new_pos in res_set else 0
        # discourage moving away from the currently best resource
        cur_self = min(md((sx, sy), r) for r in res_set) if res_set else 0
        closer = cur_self - self_best if self_best is not None else 0
        # small tie-break: keep toward center-ish (deterministic)
        center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        score = (0 if capture else 1, race, -closer, -center_bias)
        if best_score is None or score < best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]