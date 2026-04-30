def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    # Pick resource with best distance advantage to self (opponent farther is good).
    target = None
    best_adv = -10**18
    for r in resources:
        myd = man(me, r)
        opd = man(opp, r)
        adv = (opd - myd) * 1000 - myd * 2
        if adv > best_adv or (adv == best_adv and (r[0], r[1]) < (target[0], target[1]) if target else False):
            best_adv = adv
            target = r

    # If no resources (unlikely), head to farthest corner from opponent.
    if target is None:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        target = max(corners, key=lambda c: man(opp, c) - 0.5 * man(me, c))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, (0, 0))
    tx, ty = target

    # If contested (opponent closer), bias toward stepping to increase distance from opponent while still progressing.
    contested = man(me, target) > man(opp, target)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nme = (nx, ny)
        myd = abs(nx - tx) + abs(ny - ty)
        opd = abs(nx - ox) + abs(ny - oy)
        oppd_to_t = abs(ox - tx) + abs(oy - ty)

        # Move score: reduce distance to target strongly; also keep opponent away when contested.
        score = -myd * 20 + (man(opp, target) - oppd_to_t) * 6 - myd * 0.5
        if contested:
            score += opd * 2.2
        else:
            # Not contested: slightly prefer being closer to target than opponent is.
            score += (opd - man(me, target)) * 0.2

        if score > best[0]:
            best = (score, (dx, dy))

    return [best[1][0], best[1][1]]