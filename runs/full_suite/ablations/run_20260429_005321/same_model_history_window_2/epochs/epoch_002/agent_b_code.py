def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = [(p[0], p[1]) for p in observation["resources"]]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        best_score = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - cx) + abs(ny - cy)
            score = -d - 0.01 * (abs(nx - ox) + abs(ny - oy))
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    # Pick a target that we can "steal": larger distance advantage over opponent, tie by closeness to self.
    best_t = None
    best_gain = -10**18
    for tx, ty in resources:
        sg = cheb(sx, sy, tx, ty)
        og = cheb(ox, oy, tx, ty)
        gain = og - sg
        if gain > best_gain or (gain == best_gain and (sg < cheb(sx, sy, best_t[0], best_t[1]) if best_t else True)):
            best_gain = gain
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = [0, 0]
    best_score = -10**18

    # Deterministic tie-breaking: fixed delta order
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        ds = cheb(nx, ny, tx, ty)
        # Also account for blocking: prefer moving into positions that are "farther" for opponent relative to their target.
        opp_d_to_tx = cheb(ox, oy, tx, ty)

        # If there are other resources, discourage moving away from best available stealing opportunities.
        nearest_other_score = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            g = cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
            if g > nearest_other_score:
                nearest_other_score = g

        # Main objective: lower distance to our chosen target, higher opponent disadvantage.
        score = (-2 * ds) + (0.7 * (opp_d_to_tx - cheb(ox, oy, tx, ty))) + (1.2 * nearest_other_score) - 0.01 * (abs(nx - ox) + abs(ny - oy))
        # Since (opp_d_to_tx - cheb(ox, oy, tx, ty)) is always 0, keep term harmless but deterministic.

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move