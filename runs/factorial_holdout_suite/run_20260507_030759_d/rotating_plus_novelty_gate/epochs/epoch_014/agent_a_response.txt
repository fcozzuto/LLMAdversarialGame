def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    ox, oy = observation["opponent_position"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res_list = resources[:]
    res_list.sort(key=lambda r: (r[0], r[1]))

    best = None
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = 0
        # Immediate collection
        if (nx, ny) in obstacles:
            score -= 10**6
        if resources:
            if (nx, ny) in [tuple(r) for r in res_list]:
                score += 10**9
        # Competitive advantage: how much closer we are than opponent (with opponent assumed stationary)
        if res_list:
            # prioritize nearest resources, deterministically
            for rx, ry in sorted(res_list, key=lambda r: (man(nx, ny, r[0], r[1]), r[0], r[1]))[:8]:
                our_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)
                # maximize opp_d - our_d; also prefer reducing our_d
                score += (opp_d - our_d) * 1000
                score += -our_d
                # slight extra for pushing toward resources near opponent (deny)
                score += -1 if opp_d <= our_d else 0
        # Keep away from obstacles a bit (robustness)
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in obstacles:
                    score -= 3

        key = (-(score), dx, dy)  # deterministic tie-break: higher score, then smaller dx,dy? via key
        if best is None or key < best:
            best = key
            best_score = score

    # recover dx,dy from best key
    dx = best[1]
    dy = best[2]
    return [int(dx), int(dy)]