def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    remaining = int(observation.get("remaining_resource_count") or len(resources))
    phase = 0 if remaining > 6 else 1  # late-game: commit more strongly

    best = (0, 0)
    best_val = -10**18

    # Prefer targets where we can beat opponent; in late-game, push more aggressively.
    k = 1.25 + 0.35 * phase
    my_better = []
    for tx, ty in resources:
        dm = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        if dm <= do:
            my_better.append((tx, ty))
    target_pool = my_better if my_better else resources

    # Precompute distances from current positions to resources (deterministic).
    td = {}
    for tx, ty in target_pool:
        td[(tx, ty)] = (cheb(sx, sy, tx, ty), cheb(ox, oy, tx, ty))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Evaluate: choose best target for this move, then score by contest and risk.
        best_target_val = -10**18
        for tx, ty in target_pool:
            dm2 = cheb(nx, ny, tx, ty)
            do = td[(tx, ty)][1]
            dm = td[(tx, ty)][0]
            approach = dm - dm2  # positive if improved distance
            contest = do - dm2    # positive if we would be closer than opponent
            # Mild obstacle/corner bias: avoid increasing cheb to opponent corner relative to our corner.
            avoid = 0
            if (nx, ny) != (sx, sy):
                # Encourage moving toward center to reduce trapping by obstacles
                cx, cy = w // 2, h // 2
                avoid = -0.03 * cheb(nx, ny, cx, cy)

            val = k * contest + 0.55 * approach + avoid + (-0.02 * dm2)
            if val > best_target_val:
                best_target_val = val

        # Small deterministic tie-break: prefer lexicographically smallest move among equals.
        if best_target_val > best_val or (best_target_val == best_val and (dx, dy) < best):
            best_val = best_target_val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]