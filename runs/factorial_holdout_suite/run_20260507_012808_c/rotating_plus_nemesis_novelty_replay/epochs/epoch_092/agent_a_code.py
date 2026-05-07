def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0
        if sx < tx: dx = 1
        elif sx > tx: dx = -1
        dy = 0
        if sy < ty: dy = 1
        elif sy > ty: dy = -1
        return [dx, dy]

    # Choose a move that helps us beat the opponent for some nearby resource.
    best_move = (0, 0)
    best_val = -10**18
    for dx0, dy0 in deltas:
        nx, ny = sx + dx0, sy + dy0
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate limited set of closest resources to keep deterministic and fast.
        # Pick by our distance, then opponent race margin.
        scored = []
        for rx, ry in resources:
            d1 = manh(nx, ny, rx, ry)
            d2 = manh(ox, oy, rx, ry)
            scored.append((d1, d2, rx, ry))
        scored.sort(key=lambda t: (t[0], t[2], t[3], t[1]))

        take = 4 if len(scored) >= 4 else len(scored)
        val = -10**18
        for i in range(take):
            d1, d2, rx, ry = scored[i]
            # Prefer resources we can reach sooner; slightly discourage giving opponent advantage.
            race = (d2 - d1)
            # Mild preference for staying aligned toward upper-right quadrant (opponent in opposite corner).
            bias = (rx - nx) - 0.3 * (ry - ny)
            cur = 2.0 * race - 0.1 * d1 + 0.05 * bias
            if cur > val:
                val = cur

        # Secondary: avoid being too slow overall if races are similar.
        if val > best_val or (val == best_val and (abs(dx0) + abs(dy0) < abs(best_move[0]) + abs(best_move[1]))):
            best_val = val
            best_move = (dx0, dy0)

    # If all moves were blocked (shouldn't happen often), stand still.
    return [int(best_move[0]), int(best_move[1])]