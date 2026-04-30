def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        # Chebyshev for diagonal moves
        return dx if dx > dy else dy

    # If no resources, just drift away from opponent (deterministic)
    if not resources:
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (ox, oy))
            if d > best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Target selection: prioritize resources where we are (significantly) closer than opponent
    best_res = None
    best_score = -10**18
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        # Strong preference for ours-over-opp; secondary prefer closer to us
        score = (od - sd) * 2.0 - sd * 0.08
        # Mildly prefer resources not "behind" obstacles-adjacent (avoid clutter) via local penalty
        rx, ry = r
        if (rx-1, ry) in obstacles or (rx+1, ry) in obstacles or (rx, ry-1) in obstacles or (rx, ry+1) in obstacles:
            score -= 0.3
        if score > best_score:
            best_score = score
            best_res = r

    tx, ty = best_res

    # Move: go toward target, but avoid letting opponent gain a closer position to the target
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        # Prefer minimizing my distance; also avoid being adjacent to opponent unless it helps target
        adj_opp = 1 if max(abs(nx-ox), abs(ny-oy)) == 1 else 0
        score = -myd * 2.0 + (opd - myd) * 0.2 - adj_opp * (1.2 if myd > 0 else 0.3)
        candidates.append((score, -abs(nx - tx) - abs(ny - ty), dx, dy))
    candidates.sort(reverse=True)
    return [int(candidates[0][2]), int(candidates[0][3])]