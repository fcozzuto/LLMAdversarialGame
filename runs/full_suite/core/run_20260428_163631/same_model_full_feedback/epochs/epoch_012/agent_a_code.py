def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles

    if not resources:
        dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if safe(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    neigh = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def opp_reach_min(tx, ty):
        best = 10**9
        for kx, ky in neigh:
            nx, ny = ox + kx, oy + ky
            if safe(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < best: best = d
        return best if best != 10**9 else cheb(ox, oy, tx, ty)

    # Opponent static-distance baseline (refreshed each turn), for deterministic differential scoring.
    opp_min_to_any = min(opp_reach_min(rx, ry) for rx, ry in resources)

    best_move = [0, 0]
    best_score = -10**18

    # Evaluate each candidate by improving our best access compared to opponent's best access.
    # Also lightly prefer moving away from opponent to avoid being "contested" too early.
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        my_min = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        # If we step onto a resource this turn, cheb==0 dominates.
        my_dist_to_opp = cheb(nx, ny, ox, oy)

        # Predict opponent could move then take our target:
        # assume opponent's best possible min to any resource next, compare differential.
        # Use opp_min_to_any (already computed) to keep determinism and reduce compute.
        opp_metric = opp_min_to_any

        # Score: maximize advantage = (opp_best - my_best), and in ties prefer larger separation.
        score = (opp_metric - my_min) * 1000 + my_dist_to_opp

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]