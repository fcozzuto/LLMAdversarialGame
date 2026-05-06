def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = []
    for r in (observation.get("resources", []) or []):
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))
    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_from(px, py):
        my = (px, py)
        best = -10**9
        for rx, ry in resources:
            r = (rx, ry)
            my_d = man(my, r)
            opp_d = man((ox, oy), r)
            # If opponent is closer, strongly avoid to prevent handing them the grab.
            # Otherwise prefer resources we can reach first and quickly.
            lead = opp_d - my_d
            align = abs((rx - px) - (ry - py))  # smaller is better
            sc = 0
            sc += (lead * 6)
            sc += (-my_d * 2)
            sc += (-align * 0.2)
            if lead < 0:
                sc -= (abs(lead) * 12)
            # Small tie-breaker: prefer moving toward opponent-free quadrant (diagonal advance)
            sc += ((px - sx) * (rx - sx) + (py - sy) * (ry - sy)) * 0.01
            if sc > best:
                best = sc
        return best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # One-step lookahead: choose move that gives best future advantage.
        val = score_from(nx, ny)
        # If this move doesn't improve relative to staying, prefer staying less (avoid obstacle-adjacent attempts).
        if dx == 0 and dy == 0:
            val -= 0.05
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # Deterministic fallback toward the closest resource that we aren't clearly behind on.
        best = None
        for rx, ry in resources:
            my_d = man((sx, sy), (rx, ry))
            opp_d = man((ox, oy), (rx, ry))
            if opp_d < my_d:
                continue
            t = (my_d, rx, ry)
            if best is None or t < best[0]:
                best = (t, (rx, ry))
        if best is None:
            rx, ry = min(resources, key=lambda r: (man((sx, sy), r), r[0], r[1]))
        else:
            rx, ry = best[1]
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        return [dx, dy]
    return best_move