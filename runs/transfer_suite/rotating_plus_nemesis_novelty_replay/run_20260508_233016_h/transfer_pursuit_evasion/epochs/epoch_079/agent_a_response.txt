def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role") or "")
    evader = "evader" in role.lower()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    def wall_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    opp_wall = wall_dist(ox, oy)

    # If opponent is near a wall, bias along the axis that pushes into the corner (pursuit) or away from it (evasion).
    bias_x = 0
    if ox <= 1:
        bias_x = 1
    elif ox >= w - 2:
        bias_x = -1
    bias_y = 0
    if oy <= 1:
        bias_y = 1
    elif oy >= h - 2:
        bias_y = -1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        # Base: distance to opponent
        dist = abs(nx - ox) + abs(ny - oy)
        # For evader, prefer larger distance; for pursuer prefer smaller.
        base = -dist if not evader else dist

        # Secondary: avoid hugging walls too early for evader; for pursuer, prefer moves that reduce opponent wall distance.
        nd_wall = wall_dist(nx, ny)
        wall_term = 0.0
        if opp_wall <= 2:
            # Pursuer: push towards the wall/corner of opponent along biased axis.
            # Evader: do opposite to give escape room.
            wall_term = (bias_x * (nx - sx) + bias_y * (ny - sy))
            if evader:
                wall_term = -wall_term
        else:
            wall_term = (nd_wall if evader else -nd_wall) * 0.05

        # Tiebreaker: prefer moves that align with direct pursuit/evasion direction.
        align = (nx - sx) * (ox - sx) + (ny - sy) * (oy - sy)
        if evader:
            align = -align
        align_term = 0.001 * align

        score = base + wall_term + align_term

        if best_score is None:
            best_score = score
            best = [dx, dy]
        else:
            if score > best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]