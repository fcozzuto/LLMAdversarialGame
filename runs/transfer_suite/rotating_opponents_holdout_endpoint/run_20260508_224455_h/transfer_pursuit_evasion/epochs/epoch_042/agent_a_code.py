def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "escape", "coward"))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = None

    # deterministic tie-break order: keep move that appears earlier in moves list
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d = cheb(nx, ny, ox, oy)

        # secondary: avoid stepping "into" the opponent (reduces risk for pursuer; increases for evader)
        # and slightly prefer moves that increase/decrease both axes (wall-running / staying tight to corridors)
        stepx = 0 if nx == ox else (1 if nx > ox else -1)
        stepy = 0 if ny == oy else (1 if ny > oy else -1)
        align = abs((nx - ox)) + abs((ny - oy))

        # small deterministic preference to reduce cycles: prefer moving that changes either coordinate if possible
        moved = 1 if (dx != 0 or dy != 0) else 0

        if is_evader:
            # maximize distance; also try not to line up too directly with opponent
            score = (d * 1000) + (align * 2) + (moved * 3)
            # if we can keep distance while also moving away in the dominant axis, reward it
            score += (1 if (dx != 0 and (sx + dx - ox) * (sx - ox) <= 0) else 0)
            score += (1 if (dy != 0 and (sy + dy - oy) * (sy - oy) <= 0) else 0)
            better = best_score is None or score > best_score
        else:
            # minimize distance; slight reward for moving into opponent's general quadrant
            score = (-d * 1000) + (align * -1) + (moved * 3)
            # favor progress in the dominant Chebyshev axis
            score += (1 if dx == 0 or abs(nx - ox) >= abs(sx - ox) else 0)
            score += (1 if dy == 0 or abs(ny - oy) >= abs(sy - oy) else 0)
            better = best_score is None or score > best_score

        if better:
            best_score = score
            best = [dx, dy]

    # if somehow all moves are blocked (shouldn't), stay
    return best if best is not None else [0, 0]