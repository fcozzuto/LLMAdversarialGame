def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d): 
        dx = a - c
        dy = b - d
        return (dx*dx + dy*dy)  # squared euclidean

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = (10**18, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            v = dist(nx, ny, tx, ty)
            if v < best[0]:
                best = (v, (dx, dy))
        return list(best[1])

    best_move = (0, 0)
    best_val = -10**18

    # Precompute opponent distances to each resource
    opp_d = []
    for rx, ry in resources:
        opp_d.append(dist(ox, oy, rx, ry))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose resource that this candidate would "claim" best (greedy by self then relative to opponent)
        chosen = None
        chosen_score = 10**18
        ns_d_list = []
        for i, (rx, ry) in enumerate(resources):
            nd = dist(nx, ny, rx, ry)
            ns_d_list.append(nd)
            rel = nd - opp_d[i]  # smaller is better (self closer than opponent)
            # Prefer being closer to a resource, but also outpacing opponent
            key = nd * 1.0 + rel * 0.15
            if key < chosen_score:
                chosen_score = key
                chosen = (rx, ry, nd, opp_d[i])

        if chosen is None:
            continue

        rx, ry, nd, od = chosen
        # Value: primarily maximize closeness advantage; add a small tie-break for current distance
        val = (od - nd) * 1.2 - nd * 0.02

        # Small safety: prefer moves that keep some distance from obstacles (avoid trapping)
        # Count nearby obstacle cells
        adj = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0: 
                    continue
                px, py = nx + ex, ny + ey
                if (px, py) in obstacles:
                    adj += 1
        val -= adj * 0.1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_val == -10**18:
        return [0, 0]
    return [best_move[0], best_move[1]]