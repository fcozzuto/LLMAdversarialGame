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

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (0, 0)
    best_val = None

    # Limit evaluation to a few closest resources to keep it fast and deterministic
    resources_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    k = 5 if len(resources_sorted) > 5 else len(resources_sorted)
    targets = resources_sorted[:k]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Choose target that maximizes advantage: (opp_distance - my_distance)
        my_best = 10**9
        opp_best = 10**9
        advantage = -10**9
        for tx, ty in targets:
            md = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            if md < my_best:
                my_best = md
            if od < opp_best:
                opp_best = od
            adv = od - md
            if adv > advantage:
                advantage = adv

        # Additional tiebreakers encourage progress to nearest resource and away from stagnation
        dist_to_nearest = my_best
        val = (advantage * 1000) - dist_to_nearest * 10 - (abs(ox - nx) + abs(oy - ny)) * 0.001

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]