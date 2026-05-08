def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy, best_val = 0, 0, -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            continue
        if (nx, ny) in obstacles:
            continue

        cur = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # Win-next acquisition race: strongly prefer cells where opponent is farther.
            # Tie-break toward faster acquisition and slightly toward bigger "opponent delay".
            v = (od - sd) * 1000 - sd * 3

            # Additional bias: prefer resources aligned with opponent being far in Chebyshev metric.
            v -= (abs(rx - ox) + abs(ry - oy)) * 0.02
            if sd == 0:
                v += 2000  # immediate collection

            if v > cur:
                cur = v

        # If multiple moves yield similar race value, keep progress toward our best resource
        if cur > best_val + 1e-9:
            best_val = cur
            best_dx, best_dy = dx, dy
        elif abs(cur - best_val) <= 1e-9:
            if cheb(sx + dx, sy + dy, resources[0][0], resources[0][1]) < cheb(sx, sy, resources[0][0], resources[0][1]):
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]