def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    resources = [tuple(p) for p in observation.get('resources', [])]
    if not resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    best_move = None
    best_val = -1e18

    opp_pos = (ox, oy)
    self_pos = (sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        new_pos = (nx, ny)
        # Choose the resource where we are most likely to "race" the opponent.
        best_diff = -1e18
        best_d_self = 1e18
        for r in resources:
            d_self = dist(new_pos, r)
            d_opp = dist(opp_pos, r)
            diff = d_opp - d_self  # positive favors us
            if diff > best_diff:
                best_diff = diff
            if d_self < best_d_self:
                best_d_self = d_self
        # If no favorable race, just minimize distance.
        val = best_diff * 10.0 - best_d_self
        # Small tie-breaker: avoid stepping away from center when diff ties.
        val -= ((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]