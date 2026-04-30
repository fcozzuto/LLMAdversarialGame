def choose_move(observation):
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = observation["grid_width"]
    h = observation["grid_height"]

    ox = set((o[0], o[1]) for o in obstacles)
    sx, sy = self_pos
    ex, ey = opp_pos

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # chebyshev

    if resources:
        best_t = None
        best_val = None
        for r in resources:
            rs = dist(self_pos, r)
            ro = dist(opp_pos, r)
            # Prefer resources we can reach quickly, especially those where opponent is slower.
            val = rs - 0.9 * ro
            if best_val is None or val < best_val or (val == best_val and (rs < dist(self_pos, best_t) if best_t else True)):
                best_val = val
                best_t = r
        tx, ty = best_t
    else:
        # No resources visible: head toward the center.
        tx, ty = (w - 1) / 2, (h - 1) / 2

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in ox:
            continue

        if resources:
            nd = dist((nx, ny), (tx, ty))
            od = dist((nx, ny), opp_pos)
            # Primary: reduce distance to chosen target.
            # Secondary: keep distance from opponent to avoid being trapped in races.
            score = (-nd) + 0.12 * od
        else:
            # Move toward center if no resources.
            nd = max(abs(nx - tx), abs(ny - ty))
            score = -nd

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move