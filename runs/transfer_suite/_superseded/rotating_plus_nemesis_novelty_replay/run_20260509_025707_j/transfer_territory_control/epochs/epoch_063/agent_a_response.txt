def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_list = list(opp_set)
    def closest_opp_dist(x, y):
        if not opp_list:
            return 0
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    # Focus: deterministically counterclaim by stepping onto opponent territory when possible,
    # otherwise advance toward the nearest opponent cell, lightly preferring unclaimed.
    curd = closest_opp_dist(sx, sy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        score = 0.0
        if (nx, ny) in opp_set:
            score += 5.0  # immediate counterclaim / flipping target on entry
            # Prefer approaches that also reduce distance to opponent.
            score += 0.1 * (curd - closest_opp_dist(nx, ny))
        elif (nx, ny) in unclaimed:
            score += 0.8  # safer expansion when no direct flip available
            score += 0.05 * (curd - closest_opp_dist(nx, ny))
        else:
            score += 0.02 * (curd - closest_opp_dist(nx, ny))
            # Avoid wandering farther from opponent late game
            tr = observation.get("turns_remaining", 0)
            if tr <= 16:
                score -= 0.03 * max(0, closest_opp_dist(nx, ny) - curd)

        # Mild preference to avoid stepping back into our territory only when retreating
        if (nx, ny) in self_set:
            score -= 0.01

        # Deterministic tie-break: fixed ordering by move list index and then dx,dy
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if moves.index((dx, dy)) < moves.index(best_move) if best_move != (0, 0) else True:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]