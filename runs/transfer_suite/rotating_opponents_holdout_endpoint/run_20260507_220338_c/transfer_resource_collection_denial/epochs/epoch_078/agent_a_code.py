def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick resource where we have best "reach" advantage over opponent (using straight-line distance).
    best = None
    best_val = -10**18
    for t in res:
        sd = d2((sx, sy), t)
        od = d2((ox, oy), t)
        # Prefer smaller opponent distance gap (opp closer => bad); maximize our advantage.
        # Add slight tie-break toward nearer resource.
        val = (od - sd) * 1000 - sd
        if val > best_val:
            best_val = val
            best = t
    tx, ty = best

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        ns = d2((nx, ny), (tx, ty))
        no = d2((nx, ny), (ox, oy))
        # Move toward target while keeping opponent farther (shadow opponent tends to contest).
        score = -ns + 0.08 * no
        # If we can capture now, strongly prioritize.
        if (nx, ny) == (tx, ty):
            score += 10**7
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]