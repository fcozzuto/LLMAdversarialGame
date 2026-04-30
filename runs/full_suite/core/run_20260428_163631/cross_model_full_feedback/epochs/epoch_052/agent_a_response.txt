def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    my = (sx, sy)
    op = (ox, oy)

    target = None
    best_adv = -10**9
    for r in resources:
        adv = cheb(op, r) - cheb(my, r)
        # slight preference for closer overall
        adv -= 0.01 * cheb(my, r)
        if adv > best_adv:
            best_adv = adv
            target = r

    def safe(nx, ny):
        # avoid stepping adjacent (likely contested/capture mechanics)
        return not (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)

    best = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        if target is not None and not safe(nx, ny):
            continue
        cand_my = (nx, ny)
        if target is None:
            # drift toward center and away from opponent
            center = (w // 2, h // 2)
            score = -cheb(cand_my, center) + 0.3 * cheb(cand_my, op)
        else:
            # primary: reduce distance to target; secondary: increase distance from opponent
            d = cheb(cand_my, target)
            do = cheb(cand_my, op)
            score = (-10 * d) + (2 * do) + (best_adv * 0.1)
        # deterministic tie-break: prefer smaller dx, then smaller dy
        if best is None or score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    # fallback: if all "unsafe" filtered out, pick best safe-less move away from opponent
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        cand_my = (nx, ny)
        score = 2 * cheb(cand_my, op) - cheb(cand_my, (w // 2, h // 2))
        if best is None or score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]