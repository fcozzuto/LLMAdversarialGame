def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    occ = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in occ:
            continue

        # Evaluate best target resource from this move.
        local_best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)

            # Prefer resources where we are strictly closer than opponent.
            # If close, prefer smaller my_d to reach sooner.
            # Secondary: prefer changing row slightly away from opponent (denier-style).
            row_gap = abs(ry - oy)
            score = (my_d - opp_d, my_d + 0.02 * row_gap, -int(my_d == 0))

            if local_best is None or score < local_best:
                local_best = score

        if local_best is None:
            continue

        # Small preference to keep moves valid and not stall too long:
        # prefer moves that reduce distance to the currently-best resource.
        if best_score is None or local_best < best_score:
            best_score = local_best
            best = [dx, dy]

    # Fallback if all blocked (shouldn't happen often)
    return best if best in ([-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 0], [0, 1], [1, -1], [1, 0], [1, 1]) else [0, 0]