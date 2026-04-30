def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cands.append((dx, dy))
    if not cands:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_d = man(sx, sy, ox, oy)
    away_mode = opp_d <= 3

    best_dx, best_dy = 0, 0
    best_val = -10**18

    # If resources exist: compete by maximizing "how much closer we are than opponent" for some resource,
    # with a tie-break preferring distance to nearest resource and anti-collision/anti-clamp.
    if resources:
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy

            # Avoid letting opponent immediately step onto our next cell vicinity
            # (soft penalty if we're within 1 of opponent after move).
            collision_pen = -5 if man(nx, ny, ox, oy) <= 1 else 0

            # Resource competition value
            best_comp = -10**18
            best_my = 10**9
            for rx, ry in resources:
                d_my = man(nx, ny, rx, ry)
                d_op = man(ox, oy, rx, ry)
                # Also consider opponent could move one step next turn: cheap lookahead
                d_op_next = max(0, d_op - 1)
                comp = (d_op_next - d_my)  # positive => we are ahead
                if comp > best_comp:
                    best_comp = comp
                if d_my < best_my:
                    best_my = d_my

            # If opponent is close, prioritize increasing distance while still not abandoning resources entirely.
            if away_mode:
                dist_term = man(nx, ny, ox, oy)
                val = 6 * best_comp + 2 * dist_term - 0.3 * best_my + collision_pen
            else:
                # Prefer capturing soon: strongly reward being ahead on some resource, then minimize our distance
                val = 8 * best_comp - 0.9 * best_my + 1.2 * (man(nx, ny, ox, oy) - opp_d) + collision_pen
            if val > best_val:
                best_val = val
                best_dx, best_dy = dx, dy

    else:
        # No resources: run from opponent unless already far, prefer diagonals increasing distance.
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy
            val = man(nx, ny, ox, oy)
            if away_mode:
                val = 3 * val
            else:
                val = 2 * val
            if val > best_val:
                best_val = val
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]