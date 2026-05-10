def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                seen.add((x, y))
                resources.append((x, y))

    if not resources:
        return [0, 0]

    resset = set(resources)

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Anticipate contest: prefer resources we can reach sooner; if close, prefer central ones.
    best_score = -10**18
    best_move = [0, 0]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            landed = 1 if (nx, ny) in resset else 0
            my_pos = (nx, ny)

            # Evaluate best contested resource from this candidate move.
            candidate = -10**18
            for rx, ry in resources:
                rpos = (rx, ry)
                myd = cheb(my_pos, rpos)
                opd = cheb((ox, oy), rpos)
                # Higher is better
                centrality = -(((rx - center[0]) * (rx - center[0]) + (ry - center[1]) * (ry - center[1])) ** 0.5)
                score = (1000 if myd == 0 else 0) + (200 / (1 + myd)) - (180 / (1 + opd)) + 3 * centrality
                # Nudge to reduce opponent advantage when very close
                score += 10 if myd < opd else (-10 if myd > opd else 0)
                if score > candidate:
                    candidate = score

            # If we land on a resource now, strongly prefer.
            total = candidate + (500 if landed else 0)
            if total > best_score:
                best_score = total
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]