def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy))
    if not cand:
        return [0, 0]

    me = (sx, sy)
    opp = (ox, oy)

    if not resources:
        # drift toward farthest corner from opponent to reduce contest
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for dx, dy in cand:
            nn = (sx + dx, sy + dy)
            score = max(dist(nn, c) for c in corners) - dist(nn, opp)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    rem = len(resources)
    best = None
    for dx, dy in cand:
        nn = (sx + dx, sy + dy)
        me_best = None
        opp_best = None
        for r in resources:
            dm = dist(nn, r)
            do = dist(opp, r)
            if me_best is None or dm < me_best:
                me_best = dm
            if opp_best is None or do < opp_best:
                opp_best = do
        # favor moves that make nearest resource closer to us than to opponent, and that deny opponent proximity
        # tie-break deterministically by preferring smaller dm and then larger (opp_best - me_best)
        score = (opp_best - me_best) * (1.0 + 1.0 / (1 + rem)) - 0.01 * me_best
        if best is None or score > best[0] or (score == best[0] and (me_best < best[1])):
            best = (score, me_best, dx, dy)

    return [int(best[2]), int(best[3])]