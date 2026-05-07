def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def kd(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        dx = -dx if dx < 0 else dx
        dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy  # Chebyshev: matches diagonal steps

    # Choose move that maximizes our advantage to the best contested resource after the move.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy

        best_delta = -10**18
        best_selfd = 10**18
        # Compute best resource from the candidate next position.
        for r in resources:
            self_d = kd((nx, ny), r)
            opp_d = kd((ox, oy), r)
            delta = opp_d - self_d  # positive means we are closer / can win first
            if delta > best_delta or (delta == best_delta and self_d < best_selfd):
                best_delta = delta
                best_selfd = self_d

        # If we can secure a positive contest, strongly prefer those; otherwise still pick least bad.
        val = (best_delta, -best_selfd)
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]