def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    legal_deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx, dy in legal_deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not resources or not legal:
        return [0, 0]

    best = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        # Choose the resource that is best after this move, using opponent race/denial.
        local_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < do:
                key = (0, do - ds, -ds, rx, ry)  # immediate race win
            elif ds == do:
                key = (1, 0, -ds, rx, ry)      # tie; still prioritize nearer
            else:
                key = (2, do - ds, -(do - ds) * 2, -ds, rx, ry)  # denial: maximize lead of opponent while minimizing ours
            if local_best is None or key < local_best:
                local_best = key
        if local_best is None:
            continue
        # Prefer moves with better local_best; add slight bias toward reducing distance to all resources.
        overall = (local_best[0], local_best[1], local_best[2], cheb(nx, ny, sx, sy), cheb(nx, ny, ox, oy))
        if best is None or overall < best:
            best = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]