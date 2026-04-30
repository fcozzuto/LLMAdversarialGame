def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy) or w <= 0 or h <= 0:
        return [0, 0]

    # Score neighbor by how much closer we are than opponent to the same resource,
    # plus a small term that prefers safer positions (not adjacent to obstacles).
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # safety: fewer adjacent obstacles is better
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if inb(xx, yy) and (xx, yy) in obstacles:
                    adj_obs += 1

        if resources:
            local_best = -10**9
            for rx, ry in resources:
                ds = abs(nx - rx) + abs(ny - ry)
                do = abs(ox - rx) + abs(oy - ry)
                # prefer resources where we are closer; penalize when opponent is much closer
                val = (do - ds) - 0.08 * ds + 0.02 * do
                # if both close, prefer the nearer for us
                if do <= 2 and ds <= 2:
                    val -= 0.3 * (ds - do)
                if val > local_best:
                    local_best = val
            score = local_best - 0.35 * adj_obs
        else:
            # No resources: move away from opponent a bit while going toward center.
            cx, cy = w // 2, h // 2
            dopp = abs(nx - ox) + abs(ny - oy)
            dcent = abs(nx - cx) + abs(ny - cy)
            score = 0.15 * dopp - 0.01 * dcent - 0.35 * adj_obs

        key = (score, -abs(dx) - abs(dy), dx, dy)  # deterministic tiebreaks
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]