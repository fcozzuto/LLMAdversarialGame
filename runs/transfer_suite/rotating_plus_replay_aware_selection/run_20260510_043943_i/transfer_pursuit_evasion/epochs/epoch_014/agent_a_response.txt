def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = observation.get("self_role", "pursuer")
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def min_obs_dist2(x, y):
        best = 10**18
        for (bx, by) in obstacles:
            d = dist2(x, y, bx, by)
            if d < best:
                best = d
        return best if best != 10**18 else 10000

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    target_resources = observation.get("resources", []) or []
    resources = []
    for r in target_resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int):
                resources.append((rx, ry))
    has_res = len(resources) > 0

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_d = dist2(nx, ny, ox, oy)

        if self_role == "pursuer":
            # Go toward opponent; prefer tighter approach when resources exist (to avoid passive blocking).
            score = -opp_d
            if has_res:
                rbest = min(dist2(nx, ny, rx, ry) for (rx, ry) in resources)
                score += 0.01 * (-rbest)
            # Avoid stepping near obstacles when possible (prevents wall-running traps).
            score += 0.001 * (min_obs_dist2(nx, ny))
        else:
            # Evader: maximize distance; also avoid obstacles to prevent corridor lock-in.
            score = opp_d
            if has_res:
                # If far, drift toward resources slightly (deterministic), but still keep distance.
                rbest = min(dist2(nx, ny, rx, ry) for (rx, ry) in resources)
                score += 0.001 * (-rbest)
            score += 0.01 * (min_obs_dist2(nx, ny))

        if bestv is None or score > bestv or (score == bestv and (dx, dy) < best):
            bestv = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]