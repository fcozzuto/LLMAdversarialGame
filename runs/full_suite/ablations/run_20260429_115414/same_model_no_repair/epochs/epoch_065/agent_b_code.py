def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        # Contest resources: prefer where we are closer than opponent, especially if close in absolute terms.
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if our_d == 0:
                val += 10_000_000
            # Main term rewards being ahead at that resource; also prefers reducing overall distance.
            lead = opp_d - our_d
            if lead > 0:
                val += (1000 * lead) // (1 + our_d)
            else:
                val -= (300 * (-lead)) // (1 + opp_d)
            val += 40 // (1 + our_d)  # slightly prefer closer paths

        # Defensive pressure: if opponent is much closer to some resource, move toward it too.
        if resources:
            closest_opp_d = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            if closest_opp_d <= 2:
                # Nudge toward the resource(s) with minimal opponent distance.
                for rx, ry in resources:
                    if cheb(ox, oy, rx, ry) == closest_opp_d:
                        val += 500 // (1 + cheb(nx, ny, rx, ry))
                        break

        # Soft obstacle/edge bias: discourage moves that hug edges unless beneficial (deterministic via small penalty).
        edge_pen = 0
        if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
            edge_pen += 3
        val -= edge_pen

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best