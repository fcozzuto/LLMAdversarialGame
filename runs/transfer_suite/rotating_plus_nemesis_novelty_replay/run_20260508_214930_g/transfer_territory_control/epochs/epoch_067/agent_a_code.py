def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    turn = observation.get("turn_index", 0)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def clamp(v):
        return -1 if v < -1 else (1 if v > 1 else v)

    # Determine whether to prioritize expansion (early/mid) or defense (late)
    total = max(1, turn + (observation.get("turns_remaining", 0) if observation.get("turns_remaining") is not None else 0))
    late = 1 if (observation.get("turns_remaining", 0) is not None and observation.get("turns_remaining", 0) <= 12) else 0

    best = None
    best_score = -10**18
    base = abs(sx - ox) + abs(sy - oy)
    # Favor staying on same side of opponent and expanding frontiers
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0.0
        in_self = (nx, ny) in self_t
        in_opp = (nx, ny) in opp_t
        in_un = (nx, ny) in unclaimed

        if in_opp:
            # Can flip on entry: good only if it also advances toward/away from opponent as desired
            score += 220.0 * (1 + (1 if not late else 0))
            score += 6.0
        if in_un:
            score += 70.0 * (1 + (0.5 if not late else 0))
        if in_self:
            score += 12.0

        # Progress heuristic: move toward/away from opponent depending on phase
        nd = abs(nx - ox) + abs(ny - oy)
        progress = (base - nd)  # positive if closer
        if late:
            # Late: avoid getting too close; maintain distance
            score += (-progress) * 2.5
        else:
            score += progress * 2.5

        # Frontier bias: prefer cells that are not deep in opponent territory
        score -= (25.0 if in_opp else 0.0)
        if in_self:
            score += 5.0

        # Small deterministic tie-break: prefer diagonal only when it helps distance
        score += (0.3 if (ddx != 0 and ddy != 0) else 0.0)
        score += (0.01 * (nx + ny))

        if score > best_score:
            best_score = score
            best = (ddx, ddy)

    if best is None:
        return [0, 0]
    dx, dy = best
    return [clamp(int(dx)), clamp(int(dy))]