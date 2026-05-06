def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    opp_best_dist_now = min(man(ox, oy, rx, ry) for rx, ry in resources)
    # pick our target as the closest resource (keeps progress), but we primarily try to "stall" opponent by choosing moves
    # that force us to the resource line that opponent is likely to take.
    our_target = min(resources, key=lambda p: man(sx, sy, p[0], p[1]))
    tx, ty = our_target

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        our_dist = man(nx, ny, tx, ty)

        # Opponent nearest resource distance after our move (opponent position unchanged in this step):
        opp_near_dist = min(man(ox, oy, rx, ry) for rx, ry in resources)

        # "Stall" heuristic: compare how much closer our move brings us to the opponent's likely resource,
        # and how much it may contest. We model contest as decreasing opponent nearest distance to that resource.
        # Since opponent doesn't move yet, we approximate contest by evaluating which resource we are moving toward
        # relative to their current nearest.
        opp_near_res = min(resources, key=lambda p: man(ox, oy, p[0], p[1]))
        px, py = opp_near_res
        contest = man(nx, ny, px, py) - man(sx, sy, px, py)  # positive means we move away from their nearest, negative means towards

        # Score: prioritize our progress; additionally prefer moving away from their nearest resource (positive contest)
        # while slightly preferring moves that keep us away from it when contest is easy.
        score = (-our_dist) + (2.5 * contest) - (0.05 * opp_near_dist)

        if best is None or (score, dx, dy) > best:
            best = (score, dx, dy)

    return [best[1], best[2]] if best is not None else [0, 0]