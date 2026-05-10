def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    reslist = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            reslist.append((rx, ry))

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not reslist:
        dx = 0 if ox == x else (1 if ox > x else -1)
        dy = 0 if oy == y else (1 if oy > y else -1)
        return [dx, dy]

    # Deterministic move ordering to break ties
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)
    for mdx, mdy in deltas:
        nx, ny = x + mdx, y + mdy
        if not inb(nx, ny):
            nx, ny = x, y

        on_res = (nx, ny) in reslist
        # One-step local lookahead: choose target resource that maximizes lead over opponent
        cur_best = (-10**18, 10**18)
        for rx, ry in reslist:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            gain = od - sd
            # Encourage being closer overall if gains tie; also slight bias toward nearer resources
            val = gain * 1000 - sd
            if val > cur_best[0] or (val == cur_best[0] and sd < cur_best[1]):
                cur_best = (val, sd)

        # Bonus for immediate collection; additional bonus if we create/maintain a lead
        lead_bonus = 0
        if on_res:
            lead_bonus = 200000
        else:
            # Approximate "lead" of best target
            lead_bonus = (cur_best[0] // 1000) * 20

        score = cur_best[0] + lead_bonus
        if score > best[0]:
            best = (score, mdx, mdy)
    return [int(best[1]), int(best[2])]