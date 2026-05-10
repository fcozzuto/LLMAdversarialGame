def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    base = abs(sx - ox) + abs(sy - oy)
    best = (0, 0)
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        pos = (nx, ny)
        in_self = pos in self_t
        in_opp = pos in opp_t
        in_un = pos in unclaimed

        # Immediate gain/denial
        score = 0
        if in_opp:
            score += 900  # higher incentive to cut/flip
        if in_un:
            score += 70
        if in_self:
            score += 10

        # Frontier pressure: move towards cells that are farther from opponent (secure territory)
        nd = abs(nx - ox) + abs(ny - oy)
        score += (nd - base) * 6

        # Don't walk into opponent unless it gives flips/denial
        if in_opp:
            score += 15
        else:
            if abs(nx - ox) + abs(ny - oy) <= 1:
                score -= 18

        # Mild bias to continue outward expansion rather than oscillating
        if in_self and not in_un and not in_opp:
            score -= 6

        # If adjacent to opponent territory, prioritize stepping there to interrupt sweeps
        if not in_opp and nd <= 2:
            score += 5
        if in_opp and nd <= 3:
            score += 25

        if score > best_score:
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]