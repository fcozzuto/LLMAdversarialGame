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

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a small deterministic candidate set of unclaimed targets near us
    uc_list = list(unclaimed)
    uc_list.sort(key=lambda p: (md((sx, sy), p), p[1], p[0]))
    targets = uc_list[:10]

    best_move = (0, 0)
    best_score = -10**18
    base_self = (sx, sy)
    base_opp = (ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        cell = (nx, ny)

        score = 0.0
        # Territory control / capture incentives
        if cell in opp_t:
            score += 5000.0
        elif cell in unclaimed:
            score += 180.0
        elif cell in self_t:
            score += 20.0

        # Advance toward best target (claiming/unclaimed preferred)
        if targets:
            # Immediate distance after move, plus opponent distance as risk
            # Prefer targets that are relatively farther from opponent than from us
            best_t = None
            best_t_val = -10**18
            for t in targets:
                d_self = md(cell, t)
                d_opp = md(base_opp, t)
                val = (d_opp - d_self) * 3.0 - d_self * 0.5
                if val > best_t_val:
                    best_t_val = val
                    best_t = t
            if best_t is not None:
                score += best_t_val
                score += (md(cell, best_t) * -0.3)

        # Directly avoid stepping next to opponent unless capturing
        d_to_opp = md(cell, base_opp)
        if d_to_opp <= 1:
            score -= 60.0
        elif d_to_opp <= 2:
            score -= 25.0
        else:
            score += min(10.0, d_to_opp * 2.0)

        # Soft preference for moves that keep momentum (toward opponent can also be good if capture happens)
        score += (md(cell, base_opp) * -0.05)

        # Deterministic tie-break by fixed dir ordering
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]