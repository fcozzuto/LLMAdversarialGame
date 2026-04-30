def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_is_free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves_sorted = sorted(moves, key=lambda m: (m[0] == 0 and m[1] == 0, abs(m[0]) + abs(m[1]) == 0))

    # pick a target resource: prefer those we are not far behind vs opponent
    scored_targets = []
    for (rx, ry) in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive if we are closer than opponent
        # also slightly prefer nearer resources
        scored_targets.append((-(lead * 10 + (-sd)), rx, ry))
    scored_targets.sort()
    # evaluate best among top few targets for stability
    top = scored_targets[: min(4, len(scored_targets))]
    best = None
    best_dxdy = [0, 0]

    # compute candidate scores for next move
    for dx, dy in moves_sorted:
        nx, ny = sx + dx, sy + dy
        if not step_is_free(nx, ny):
            continue

        # block/contest: how close we are to the opponent's best target after they move
        # approximated by distance from next position to each resource we might contest.
        move_score = 0
        for _, rx, ry in top:
            sd_next = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # being closer than opponent is good; getting closer fast is good
            move_score += (od - sd_next) * 12 - sd_next * 2

        # obstacle/opponent proximity: avoid moving into positions that let opponent instantly claim
        opp_claim = 0
        for (rx, ry) in resources:
            od = cheb(ox, oy, rx, ry)
            od1 = cheb(nx, ny, rx, ry)
            # if we would be farther than them by a lot, and also close to them contesting, discourage
            if od - od1 >= 2:
                opp_claim -= 1
        move_score += opp_claim

        # slight preference to not stay still
        if dx == 0 and dy == 0:
            move_score -= 3

        if best is None or move_score > best:
            best = move_score
            best_dxdy = [dx, dy]

    return best_dxdy