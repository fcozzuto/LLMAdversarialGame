def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    if (sx, sy) in set(resources) or not resources:
        return [0, 0]

    def king(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Primary phase: sprint to the closest resource, but prefer ones the opponent is less likely to reach.
    # Switch only when resources are few to increase denial pressure.
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    deny = 1.0 if rem <= 5 else 0.25

    best = None
    for rx, ry in resources:
        sd = king(rx, ry, sx, sy)
        od = king(rx, ry, ox, oy)
        # Prefer closer for us; additionally prefer farther for opponent.
        key = (sd + deny * (-od), sd, -od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns = king(nx, ny, tx, ty)
        # Tiny tie-break to keep some separation from opponent.
        sep = king(nx, ny, ox, oy)
        k = (ns, -sep, dx, dy)
        if k < best_move:
            best_move = k
    dx, dy = best_move[2], best_move[3]
    if (sx + dx, sy + dy) in obstacles or dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]