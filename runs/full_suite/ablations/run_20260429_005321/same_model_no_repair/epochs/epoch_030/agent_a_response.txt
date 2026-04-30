def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    obs = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def obs_pen(x, y):
        if not obstacles:
            return 0
        if (x, y) in obs:
            return 10**6
        # penalize closeness to obstacles
        p = 0
        for ex, ey in obstacles:
            d = max(abs(x - ex), abs(y - ey))
            if d == 0:
                p += 10**6
            elif d == 1:
                p += 200
            elif d == 2:
                p += 60
            elif d == 3:
                p += 15
        return p

    # Pick target that maximizes being earlier than opponent; fallback to nearest.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # advantage: positive if we are closer
        adv = do - ds
        # primary: large advantage; secondary: smaller ds; tertiary: slight favor to center
        center_bonus = - (abs(rx - (gw - 1) / 2) + abs(ry - (gh - 1) / 2))
        score = (adv * 1000) - ds * 5 + center_bonus - obs_pen(rx, ry) * 0.01
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best

    # Greedy step toward target; if candidate is bad (blocked/obstacle-adjacent), try alternatives.
    candidates = []
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    step_dirs = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    seen = set()
    for ddx, ddy in step_dirs:
        if (ddx, ddy) in seen:
            continue
        seen.add((ddx, ddy))
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        nds = man(nx, ny, tx, ty)
        # also prefer moves that keep/extend advantage vs opponent
        ndo = man(nx + 0, ny + 0, tx, ty)  # same point; will evaluate opponent distance to target separately
        opp_to = man(ox, oy, tx, ty)
        my_adv_after = opp_to - nds
        cand_score = my_adv_after * 1000 - nds * 3 - obs_pen(nx, ny)
        candidates.append((cand_score, ddx, ddy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]