def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((a, b) for a, b in obstacles)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = -10**18

    # Precompute nearest obstacle distance for shaping
    obst = list(obs_set)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        # Competitive targeting: pick resource where we are relatively closer vs opponent
        if resources:
            target_score = 10**18
            target_dist = 10**18
            for rx, ry in resources:
                sd = dist2(nx, ny, rx, ry)
                od = dist2(ox, oy, rx, ry)
                # Lower is better: prefer resources where we are closer than opponent
                rel = sd - od
                # Small tie-break towards actually reaching
                val = rel * 2 + sd * 0.02
                if val < target_score:
                    target_score = val
                    target_dist = sd
        else:
            target_dist = dist2(nx, ny, ox, oy)

        # Obstacle proximity penalty
        prox = 0
        if obst:
            md = 10**18
            for bx, by in obst:
                md = min(md, dist2(nx, ny, bx, by))
            # Penalize being adjacent (md==1 or 2-ish)
            prox = -max(0, 9 - md)

        # Opponent distance: encourage closing when targeting is neutral
        oppd = dist2(nx, ny, ox, oy)
        # Main score: prioritize target distance, relative advantage, and proximity to opponent slightly
        score = -target_dist * 1.0 + prox - oppd * 0.01

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback: stay still if all moves invalid
    return [0, 0]