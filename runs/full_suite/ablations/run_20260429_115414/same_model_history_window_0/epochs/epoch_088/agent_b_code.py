def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((a, b) for a, b in obstacles)
    res_set = set((a, b) for a, b in resources)

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return (dx * dx + dy * dy) ** 0.5

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -1e18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        if (nx, ny) in res_set:
            score = 1e9 - 0.001 * dist(nx, ny, ox, oy)
        else:
            # Choose a resource where we are (materially) closer than the opponent, and where opponent is farther.
            score = -0.02 * dist(nx, ny, ox, oy)  # keep some pressure/avoid being trapped
            best_res = -1e18
            for rx, ry in resources:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                if (rx, ry) in obs_set:
                    continue
                # Core: win races by being closer; punish long commitments.
                v = (do - ds) - 0.08 * ds + 0.02 * do
                # Obstacle proximity penalty (deterministic local check)
                for ax in (rx - 1, rx, rx + 1):
                    for ay in (ry - 1, ry, ry + 1):
                        if (ax, ay) in obs_set:
                            v -= 0.3
                if v > best_res:
                    best_res = v
            score += best_res
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]