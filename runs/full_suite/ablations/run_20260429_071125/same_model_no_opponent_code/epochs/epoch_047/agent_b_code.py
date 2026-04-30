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

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    aggressive = rem >= 6
    avoid_opp = rem <= 4

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        opp_cheb = cheb(nx, ny, ox, oy)
        val = 0

        # Optional: if endgame, get farther from opponent to reduce blocking via collisions
        if avoid_opp:
            val += opp_cheb * 0.15

        if resources:
            # Score best target deterministically: reward being closer than opponent, penalize if not.
            # Also slightly prefer nearer resources to avoid dithering.
            target_best = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # if I'm closer, strongly prefer; otherwise avoid unless it's the only option
                rel = opd - myd  # positive => I'm closer
                t = rel * (2.2 if aggressive else 1.6) - myd * 0.35
                # mild obstacle discouragement near edges handled implicitly by move validity
                if aggressive and rel <= 0:
                    t -= 0.8
                target_best = t if t > target_best else target_best
            val += target_best
        else:
            # No resources visible: drift toward center
            cx, cy = w // 2, h // 2
            val += -cheb(nx, ny, cx, cy) * 0.5

        # Ensure some movement consistency: prefer moves that make progress to chosen direction
        val += -cheb(nx, ny, ox, oy) * 0.05

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]