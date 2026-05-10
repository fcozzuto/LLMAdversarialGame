def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid_resources = [(rx, ry) for rx, ry in resources if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles]
    if not valid_resources:
        return [0, 0]

    # Pick a target that we are relatively closer to than the opponent (or at least not much farther).
    best = None
    for rx, ry in valid_resources:
        dS = dist(sx, sy, rx, ry)
        dO = dist(ox, oy, rx, ry)
        adv = dO - dS
        if best is None or adv > best[0] or (adv == best[0] and dS < best[1]):
            best = (adv, dS, rx, ry)
    tx, ty = best[2], best[3]

    # Evaluate each move: maximize advantage after move, then minimize distance to the chosen target,
    # then prefer moves that reduce opponent's ability to reach nearby resources sooner.
    def move_score(nx, ny):
        dS_t = dist(nx, ny, tx, ty)
        dO_t = dist(ox, oy, tx, ty)
        score = (dO_t - dS_t) * 10 - dS_t

        # Resource contest check (small lookahead without full search)
        best_adv_against = -10**9
        best_opp_gain = 10**9
        for rx, ry in valid_resources:
            if (rx, ry) == (nx, ny):
                best_adv_against = 10**6
                break
            dS = dist(nx, ny, rx, ry)
            dO = dist(ox, oy, rx, ry)
            adv = dO - dS
            if adv > best_adv_against:
                best_adv_against = adv
            # How much better the opponent is on that resource (lower is better for us)
            opp_gain = dS - dO  # negative means opponent closer
            if opp_gain < best_opp_gain:
                best_opp_gain = opp_gain

        score += best_adv_against * 2
        score += best_opp_gain  # penalize being closer for opponent (more negative)
        return score

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = move_score(nx, ny)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]