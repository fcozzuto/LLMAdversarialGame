def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    # If opponent is very close, prioritize escaping and holding distance.
    close = kdist(sx, sy, ox, oy) <= 2

    # Deterministic tie-breaker ordering: center-ish first when scores tie.
    center_x = (w - 1) // 2
    center_y = (h - 1) // 2

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Hard penalty for stepping adjacent to obstacle-like area around opponent (corner guarding).
        opp_d = kdist(nx, ny, ox, oy)

        val = 0.0
        if close:
            # Escape: maximize distance from opponent, but still make progress to a resource.
            val += opp_d * 40.0
            # Small preference to move toward center to reduce being cornered.
            val += (7 - kdist(nx, ny, center_x, center_y)) * 1.5
        else:
            # General: resource race.
            if resources:
                for rx, ry in resources:
                    our_d = kdist(nx, ny, rx, ry)
                    opp_resource_d = kdist(ox, oy, rx, ry)
                    # Big reward only if we are at least competitive.
                    if our_d < opp_resource_d:
                        val += (opp_resource_d - our_d) * 18.0
                    # Also reward being closer to resources than opponent, even if not winning.
                    val += (opp_resource_d - our_d) * 2.0

            # Mild preference for moving away from being trapped by the opponent.
            val += (opp_d - kdist(sx, sy, ox, oy)) * 3.0

        # Avoid being too close when not already escaping.
        if opp_d <= 1:
            val -= 80.0

        # Extra weight for landing on a resource square.
        for rx, ry in resources:
            if nx == rx and ny == ry:
                val += 200.0

        # Deterministic tie-breaker: prefer closer to center when equal.
        val += -0.01 * kdist(nx, ny, center_x, center_y)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            # Compare lexicographically on move preference (center-ish then staying still).
            pref = 1 if (dx == 0 and dy == 0) else 0
            best_pref = 1 if (best_move[0] == 0 and best_move[1] == 0) else 0
            if pref < best_pref:
                best_move = [dx, dy]

    return best_move