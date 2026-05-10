def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def center_bias(nx, ny):
        return -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

    # If we can steal immediately, do it. Otherwise, expand to unclaimed, and then reinforce.
    best_move = [0, 0]
    best_score = -10**30
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        score = 0.0

        if (nx, ny) in oppT:
            score += 30.0  # strong steal pressure

        if (nx, ny) in unclaimed:
            score += 8.0

        if (nx, ny) in selfT:
            score -= 1.5  # prefer expansion over recycling

        score += 0.25 * center_bias(nx, ny)

        # Local frontier advantage: prefer cells adjacent to our territory but also not fully surrounded by it.
        adj_ours = 0
        adj_unclaimed = 0
        adj_opps = 0
        for ddx, ddy in dirs:
            if ddx == 0 and ddy == 0:
                continue
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                if (ax, ay) in selfT:
                    adj_ours += 1
                if (ax, ay) in unclaimed:
                    adj_unclaimed += 1
                if (ax, ay) in oppT:
                    adj_opps += 1

        score += 1.0 * adj_unclaimed + 0.6 * adj_opps
        score += 0.15 * adj_ours

        # Slightly avoid staying still unless it has best score.
        if dx == 0 and dy == 0:
            score -= 0.2

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move