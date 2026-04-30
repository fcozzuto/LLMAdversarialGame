def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx if dx >= 0 else -dx if False else abs(dx)

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Pick target resource we are most advantaged for (opponent further than us), tie-break by closeness to us.
    target = None
    best = None
    for r in resources:
        sd = dist(self_pos, r)
        od = dist(opp_pos, r)
        advantage = od - sd  # higher means we are closer
        # Penalize if opponent is already at the resource (or will get there first); reward positive advantage.
        score = advantage * 100 - sd
        if best is None or score > best:
            best = score
            target = r

    # If no resources, move toward center while keeping some distance from opponent.
    if target is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            dcent = dist((nx, ny), (cx, cy))
            dopp = dist((nx, ny), opp_pos)
            val = (dopp * 3) - dcent
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Move greedily toward chosen target, but avoid squares that let opponent get significantly closer.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = dist((nx, ny), target)
        op_d = dist(opp_pos, target)
        # If we step closer to target while opponent also steps (indirectly), prefer actions that keep their relative timing worse.
        my_to_opp = dist((nx, ny), opp_pos)
        val = (-my_d * 10) + ((op_d - my_d) * 5) + my_to_opp
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]