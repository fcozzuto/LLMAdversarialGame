def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        # deterministic patrol: head toward center-ish
        tx, ty = w // 2, h // 2
        candidates = []
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dist((nx, ny), (tx, ty)), nx, ny, dx, dy))
            else:
                candidates.append((10**9, nx, ny, dx, dy))
        candidates.sort()
        return [candidates[0][3], candidates[0][4]]

    # choose target resource favoring states where we are (or can become) closer than opponent
    best = None
    for rx, ry in resources:
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        # deterministic tie-break: prioritize smaller effective value
        # effective = our distance minus fraction of opponent advantage
        eff = d1 - (d2 * 0.35)
        key = (eff, d1, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # Evaluate candidate moves by how much they reduce distance to target, with obstacle penalty and opponent pressure
    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            score = -10**9
        else:
            d_now = dist((sx, sy), (tx, ty))
            d_new = dist((nx, ny), (tx, ty))
            progress = d_now - d_new
            # discourage moving into opponent's immediate vicinity
            opp_d = dist((nx, ny), (ox, oy))
            opp_pen = -0.15 * opp_d
            # slight bias to avoid oscillation: prefer moves that keep heading forward (toward target)
            heading = -0.01 * (d_new + (abs(nx - tx) - abs(sx - tx))**2 if sx != tx else abs(ny - ty) - abs(sy - ty))
            score = progress + opp_pen + heading
        if score > best_move[0]:
            best_move = (score, dx, dy)
        elif score == best_move[0]:
            # deterministic tie-break: smallest dx then dy
            if dx < best_move[1] or (dx == best_move[1] and dy < best_move[2]):
                best_move = (score, dx, dy)

    return [int(best_move[1]), int(best_move[2])]