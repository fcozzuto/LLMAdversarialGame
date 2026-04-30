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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return -0.02 * dist(int(round(x)), int(round(y)), int(round(cx)), int(round(cy)))

    if not resources:
        tx, ty = int((w - 1) // 2), int((h - 1) // 2)
        bestd, bestm = 10**9, [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, tx, ty)
            if d < bestd:
                bestd, bestm = d, [dx, dy]
        return bestm

    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Score: prioritize resources we can reach sooner than opponent; also slightly prefer closeness.
        # Use top-3 targets deterministically.
        scored = []
        for (rx, ry) in resources:
            d_me = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            # Positive if we are closer; discourage giving opponent big advantage.
            rel = d_op - d_me
            gain = 3.0 * rel - 0.25 * d_me
            scored.append(gain)

        scored.sort(reverse=True)
        topk = scored[:3]
        val = sum(topk) + center_bias(nx, ny)

        # If we are not winning any target, bias toward the resource that reduces opponent advantage most.
        if topk and topk[0] <= 0:
            # Choose resource maximizing reduction in opponent distance gap.
            best_rel = -10**9
            for (rx, ry) in resources:
                d_me = dist(nx, ny, rx, ry)
                d_op = dist(ox, oy, rx, ry)
                rel = d_op - d_me
                if rel > best_rel:
                    best_rel = rel
            val += 2.0 * best_rel

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move