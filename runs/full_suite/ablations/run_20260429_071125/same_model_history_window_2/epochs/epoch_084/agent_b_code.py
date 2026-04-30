def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Center bias + opponent interference: prioritize resources where we are closer than opponent.
    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0

    best = None
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        # If we can capture a resource immediately, take it.
        immediate = 0
        score = 0.0
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            if d_self == 0:
                immediate = 1
                break
        if immediate:
            return [dx, dy]

        # Evaluate best target with opponent-aware advantage.
        # Higher is better.
        best_target = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)

            # Advantage term: prefer targets where opponent is farther.
            adv = d_opp - d_self  # positive => we are closer
            # Progress term: prefer smaller d_self (faster reach).
            prog = -d_self

            # Mild center bias to avoid corner-trapping into stalemates.
            cb = -((nx - center_x) ** 2 + (ny - center_y) ** 2) / (w * h)

            # Combine: advantage dominates slightly, then progress.
            val = 3.0 * adv + 1.5 * prog + 0.05 * cb
            if val > best_target:
                best_target = val

        # Secondary: avoid moving into "resource dead-ends" near opponent by limiting how close we get to opponent.
        d_op = cheb(nx, ny, ox, oy)
        score = best_target + 0.03 * d_op

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]