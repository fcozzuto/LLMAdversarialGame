def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        ad = a - c
        if ad < 0: ad = -ad
        bd = b - d
        if bd < 0: bd = -bd
        return ad if ad > bd else bd

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = (-1e18, 0, 0)
        for dx, dy, nx, ny in moves:
            score = -(abs(nx - tx) + abs(ny - ty))
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_val = -1e18
    best_dx, best_dy = 0, 0

    for dx, dy, nx, ny in moves:
        dmin = 10**9
        dopp_min = 10**9
        block = 0
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            if ds < dmin:
                dmin = ds
            if do < dopp_min:
                dopp_min = do
            if ds <= do:
                block += 1
        opp_dist = dist(nx, ny, ox, oy)
        center = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * 1e-3
        val = (-dmin) + 0.25 * dopp_min + 0.15 * block + 0.01 * opp_dist + center
        # If we can immediately take a resource, strongly prefer it.
        if any(dist(nx, ny, rx, ry) == 0 for rx, ry in resources):
            val += 1000.0
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]