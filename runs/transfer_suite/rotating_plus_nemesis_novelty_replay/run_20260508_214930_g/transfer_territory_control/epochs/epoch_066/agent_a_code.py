def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = (0, 0)
    best_score = -10**18

    base_opp = abs(sx - ox) + abs(sy - oy)
    my_adv = observation.get("self_territory_count", len(self_t)) - observation.get("opponent_territory_count", len(opp_t))

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0.0

        if (nx, ny) in opp_t:
            score += 900.0  # prioritize flipping
        elif (nx, ny) in unclaimed:
            score += 70.0

        if (nx, ny) in self_t:
            score += 12.0
        else:
            score += 2.0

        # Push toward center (opponent tends to claim center)
        score += -1.6 * (abs(nx - cx) + abs(ny - cy))

        # Keep distance advantage / avoid getting too close to opponent's territory
        opp_d = abs(nx - ox) + abs(ny - oy)
        score += (opp_d - base_opp) * 1.2

        # If we are behind, be more aggressive near opponent territory
        if my_adv < 0:
            if (nx, ny) in opp_t:
                score += 1200.0
            else:
                score += -0.8 * (opp_d)

        # Deterministic tie-break: prefer moves that increase our territory footprint
        if score > best_score:
            best_score = score
            best = (ddx, ddy)
        elif score == best_score:
            if (ddx, ddy) < best:
                best = (ddx, ddy)

    return [int(best[0]), int(best[1])]