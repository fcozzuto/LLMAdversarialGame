def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Sort for deterministic tie-breaking
    dirs = sorted(dirs, key=lambda t: (t[0], t[1]))

    opp_cheb_to_best = []
    for (rx, ry) in resources:
        opp_cheb_to_best.append(cheb(ox, oy, rx, ry))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Score by best resource we can reach from next step.
        # Prefer resources where we are not worse than opponent, and closer to opponent to contest,
        # but also keep some separation to avoid being "bumped" off tempo.
        max_res_score = -10**18
        for i, (rx, ry) in enumerate(resources):
            myd = cheb(nx, ny, rx, ry)
            opd = opp_cheb_to_best[i]
            # If opponent already closer, only go if we can still reduce the gap.
            gap = opd - myd
            s = 20 * gap - myd
            if (nx, ny) == (rx, ry):
                s += 1000
            max_res_score = s if s > max_res_score else max_res_score

        # Small positional preference: move away from opponent a bit unless contesting well.
        opd_now = cheb(nx, ny, ox, oy)
        val = max_res_score + 0.5 * opd_now
        # Discourage unnecessary staying when there are other reachable resources.
        if (dx, dy) == (0, 0) and resources:
            val -= 3

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]