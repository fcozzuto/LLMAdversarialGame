def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**18
    best_center = 10**18

    # Evaluate each move by best "win likelihood" resource; deterministic tie-break by center closeness then my_dist.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_local_adv = -10**18
        best_local_my_dist = 10**18
        for rx, ry in res:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = (opp_d - my_d) * 1000  # big weight: contested resources
            # Prefer getting to the same good resource quickly
            score = adv - my_d
            if score > best_local_adv or (score == best_local_adv and my_d < best_local_my_dist):
                best_local_adv = score
                best_local_my_dist = my_d

        center_dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if best_local_adv > best_score or (best_local_adv == best_score and center_dist < best_center):
            best_score = best_local_adv
            best_center = center_dist
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]