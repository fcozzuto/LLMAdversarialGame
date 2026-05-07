def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))

    best_move = (0, 0, sx, sy)
    best_val = -10**9
    # Deterministic tie-break: prefer smaller dx, then smaller dy, then stay
    for dx, dy, nx, ny in sorted(moves, key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1])):
        val = 0
        # Focus on the single resource with best "relative arrival" from this next position
        best_r = -10**9
        for rx, ry in resources:
            my_t = cheb(nx, ny, rx, ry)
            op_t = cheb(ox, oy, rx, ry)
            if my_t <= op_t:
                # Can match/beat opponent: strongly prefer closer equality, then earlier
                rel = op_t - my_t
                score = 50 + 10 * rel - my_t
            else:
                # If opponent is earlier, we still contest but at reduced value
                rel = my_t - op_t
                score = -20 - 5 * rel - my_t
            if score > best_r:
                best_r = score
        val = best_r
        if val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]