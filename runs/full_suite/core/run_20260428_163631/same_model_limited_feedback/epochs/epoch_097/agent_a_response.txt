def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for diagonal

    if resources:
        best = None
        # Pick the move that improves best "we are closer than opponent" target.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            cur = [nx, ny]
            # If we can step onto a resource, do it immediately.
            if (nx, ny) in set(tuple(r) for r in resources):
                return [dx, dy]
            best_val = -10**9
            for r in resources:
                rx, ry = r
                if (rx, ry) == (nx, ny):
                    continue
                sd = dist(cur, r)
                od = dist([ox, oy], r)
                # Prefer resources where we are ahead; if tied, prefer nearer.
                val = (od - sd) * 10 - sd
                # Small tie-break: prefer moving toward the resource's direction.
                val += -((rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)) * 0.001
                if val > best_val:
                    best_val = val
            # Also slightly discourage moving toward opponent (keeps options open).
            opp_pen = dist(cur, [ox, oy]) * -0.05
            total = best_val + opp_pen
            if best is None or total > best[0] or (total == best[0] and (dx, dy) < best[1]):
                best = (total, (dx, dy))
        if best is not None:
            return [best[1][0], best[1][1]]

    # Fallback: move to reduce distance to opponent or stay if blocked.
    bestd = None
    bestmove = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = dist([nx, ny], [ox, oy])
        if bestd is None or d < bestd or (d == bestd and (dx, dy) < bestmove):
            bestd = d
            bestmove = (dx, dy)
    if inside(sx, sy):
        return [bestmove[0], bestmove[1]]
    # If even current pos is invalid (shouldn't happen), return stay.
    return [0, 0]