def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic "target denial": pick targets where we are closer than the opponent.
    cand_targets = resources if len(resources) <= 6 else resources[:6]

    best_move = [0, 0]
    best_val = -10**18
    fallback = (w // 2, h // 2)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            local_best = -10**18
            for rx, ry in cand_targets:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # High value if we can beat opponent to the target; slight tie-break by being closer.
                rel = do - ds
                # Avoid moving away from resources too much
                stay_bias = -0.05 * cheb(nx, ny, sx, sy)
                val = 3.0 * rel + (-0.01 * ds) + stay_bias
                # If opponent is very close, prioritize blocking-like behavior
                if do <= 2 and ds <= 3:
                    val += 1.0
                if val > local_best:
                    local_best = val
            # If our chosen move reaches a resource, strongly favor it
            if (nx, ny) in resources:
                local_best += 10.0
            val = local_best
        else:
            # No resources: move toward center while keeping away from obstacles is implicit via validity checks.
            val = -cheb(nx, ny, fallback[0], fallback[1]) + 0.001 * cheb(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]