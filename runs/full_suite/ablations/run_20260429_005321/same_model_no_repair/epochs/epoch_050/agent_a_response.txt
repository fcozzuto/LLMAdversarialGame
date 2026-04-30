def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick best resource considering who reaches it first.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        # Encourage taking resources we can reach first, but keep some pressure when behind.
        score = (od - sd) * 200 - sd * 3 - (1 if (rx, ry) in obstacles else 0)
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t

    # Greedy step toward target, but evaluate all legal moves for safety.
    best_move = [0, 0]
    best_move_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            val = -10**18
        else:
            # Prefer reducing distance to target and improving "lead" on resources.
            d_to_t = king_dist(nx, ny, tx, ty)
            sd_next = king_dist(nx, ny, tx, ty)
            # Look at a few best candidate resources by relative advantage.
            lead_sum = 0
            best_rel = -10**18
            worst_rel = 10**18
            for rx, ry in resources:
                sd = king_dist(nx, ny, rx, ry)
                od = king_dist(ox, oy, rx, ry)
                rel = od - sd
                if rel > best_rel:
                    best_rel = rel
                if rel < worst_rel:
                    worst_rel = rel
                # Only count strong relative advantages.
                if rel > 0:
                    lead_sum += rel
            # Balance: take immediate target progress plus strong lead pressure.
            val = -d_to_t * 6 + best_rel * 120 + lead_sum * 2 - sd_next * 1
        if val > best_move_val:
            best_move_val = val
            best_move = [dx, dy]

    # Determinism tie-break: if still ambiguous, moves list order is fixed and first max stays.
    return best_move