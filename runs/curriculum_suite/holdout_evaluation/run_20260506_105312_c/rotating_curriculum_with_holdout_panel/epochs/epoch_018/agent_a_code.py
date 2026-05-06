def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Choose a move by maximizing "gain": resources where we are closer than opponent, plus some denial pressure.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = -0.01 * cheb(nx, ny, sx, sy)  # tiny preference to not waste steps

        # Denial: prefer moves that get closer to a resource the opponent can reach quickly.
        opp_pressure = 0.0

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # If we can beat them to the resource, value increases sharply.
            diff = opd - myd
            if diff >= 1:
                # Prefer closer resources too, but don't overfocus on far ones.
                val += 50.0 * diff - 0.5 * myd
            else:
                # If opponent is ahead, attempt to deny by approaching those resources.
                if opd < myd:
                    # Opponent reachability to this resource.
                    opp_pressure += max(0.0, (10.0 - opd))
                    # Also make approaching opponent-ahead resources slightly beneficial.
                    val += 2.0 * (opd - myd)  # negative or small; still can be overridden by other resources

        # Add denial term: if opponent has easy targets, move toward reducing their options.
        val += 0.05 * opp_pressure

        # Small repulsion from opponent to avoid easy denial traps.
        val -= 0.02 * cheb(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    # If all candidate moves were blocked (should be rare), stay.
    return [int(best[0]), int(best[1])]