def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
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
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 + d2

    def closer_moves(px, py, tx, ty):
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        return dx, dy

    my_best = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    opp_best = min(resources, key=lambda r: man(ox, oy, r[0], r[1]))

    # If we are likely to lose the nearest contested resource, switch to an alternative.
    contest = (my_best == opp_best)
    if contest:
        # Choose resource maximizing (our lead) = (oppDist - myDist), tie-break by our distance.
        rx, ry = max(resources, key=lambda r: (man(ox, oy, r[0], r[1]) - man(sx, sy, r[0], r[1]), -man(sx, sy, r[0], r[1])))
        tx, ty = rx, ry
    else:
        # Otherwise, occasionally race opponent by aiming for whichever we can reach earlier than they can.
        scored = []
        for r in resources:
            md = man(sx, sy, r[0], r[1])
            od = man(ox, oy, r[0], r[1])
            # Prefer resources we can arrive at sooner; also slight push toward center to avoid dead zones.
            center_bonus = -man(r[0], r[1], (w - 1) // 2, (h - 1) // 2)
            scored.append((od - md, md, -center_bonus, r))
        _, _, _, (tx, ty) = max(scored)

    # Obstacle-avoidance for the immediate step: try the move that reduces distance to (tx,ty) while not stepping into obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = man(sx, sy, tx, ty)
    best = (10**9, 10**9, 0)  # (remaining_dist, obstacle_penalty, tie)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        obstacle_pen = 1 if (nx, ny) in obstacles else 0
        nd = man(nx, ny, tx, ty)
        # Prefer reduced distance, then non-obstacle, then deterministic tie by direction toward opponent (diagonal probe bias).
        probe = -man(nx, ny, ox + (1 if ox < tx else (-1 if ox > tx else 0)), oy + (1 if oy < ty else (-1 if oy > ty else 0)))
        key = (nd, obstacle_pen, probe)
        if key < best:
            best = key
            best_move = (dx, dy)

    # If all candidate moves were out-of-bounds (unlikely), stay.
    return [int(best_move[0]), int(best_move[1])]