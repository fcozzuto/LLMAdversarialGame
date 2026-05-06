def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Choose a contest target: prefer resources we can reach at least as well as opponent, otherwise contest the closest gap.
    best = None
    best_val = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # We want (ds - do) small; break ties by ds, then position.
        val = (ds - do, ds, rx, ry)
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    # "New" policy: greedy movement that simultaneously (a) advances to target, (b) keeps distance from opponent,
    # (c) avoids stepping onto obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            score = -10**9
        else:
            d_to_target = man(nx, ny, tx, ty)
            d_to_opp = man(nx, ny, ox, oy)
            # Encourage getting closer to target and farther from opponent.
            # Extra weight to "not get cornered" near opponent.
            score = (-d_to_target * 3) + (d_to_opp * 2)
            # Slight preference for reducing opponent's closest distance-to-target (move that increases their burden)
            d_opp_to_target = man(ox, oy, tx, ty)
            score += (d_opp_to_target - man(ox, oy, tx, ty)) * 0.0
            # Deterministic tie-break: prefer moves that reduce own distance, then lexicographic dx,dy
            score -= (abs(dx) + abs(dy)) * 0.01
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]