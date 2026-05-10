def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) and ("pursuer" not in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y, tx, ty):
        ax = abs(x - tx); ay = abs(y - ty)
        return ax if ax > ay else ay

    def dist_to_wall(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    best = (0, 0); best_score = -10**18 if i_am_evader else 10**18

    # Heuristic: pursuer minimizes distance; also "walls" the opponent by preferring moves that put the opponent closer to a border after it advances.
    # Evader maximizes distance; also prefers moving toward the farthest corner.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)

        if i_am_evader:
            tie = -(abs(nx - far_corner[0]) + abs(ny - far_corner[1]))
            score = d * 100000 + tie
            if score > best_score:
                best_score = score; best = (dx, dy)
        else:
            # Predict opponent likely next step direction (zigzag proxy): use sign of relative position.
            px = 0 if ox == nx else (1 if ox < nx else -1)
            py = 0 if oy == ny else (1 if oy < ny else -1)
            # Walling metric: smaller dist_to_wall means opponent closer to wall (good for pursuer).
            # We approximate by evaluating where opponent might be after a pursuer move.
            next_ox = ox + px; next_oy = oy + py
            if not (0 <= next_ox < w and 0 <= next_oy < h and (next_ox, next_oy) not in obstacles):
                next_ox, next_oy = ox, oy
            wall = -dist_to_wall(next_ox, next_oy)
            # Strong priority on immediate capture (distance 0), then distance reduction, then walling.
            score = d * 1000 + (-wall)
            if score < best_score:
                best_score = score; best = (dx, dy)

    return [int(best[0]), int(best[1])]