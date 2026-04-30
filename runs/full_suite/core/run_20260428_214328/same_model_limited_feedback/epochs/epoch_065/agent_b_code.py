def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for diagonal steps

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    # Determine a "contested" resource we are currently closer to than the opponent.
    contested = []
    for r in resources:
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        if myd < opd:
            contested.append((opd - myd, r, myd, opd))
    contested.sort(reverse=True)
    top_r = contested[0][1] if contested else None

    # If no clear advantage, focus on the globally best resource for us (closest).
    if top_r is None and resources:
        top_r = min(resources, key=lambda r: dist((sx, sy), r))

    # If still none (shouldn't happen), move toward opponent direction to gain symmetry breaking.
    if top_r is None:
        tx = 1 if ox > sx else (-1 if ox < sx else 0)
        ty = 1 if oy > sy else (-1 if oy < sy else 0)
        return [tx, ty]

    # Evaluate each legal move by how much closer it makes us to top contested goal
    # and by how it improves our lead over the opponent on any resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)

        # Lead potential: prefer moves that maximize (opp_dist - my_dist)
        lead = -10**6
        for r in resources:
            myd = dist(my_pos, r)
            opd = dist((ox, oy), r)
            v = opd - myd
            if v > lead:
                lead = v

        # Primary: lead; Secondary: distance to target; Tertiary: move to break ties using opponent separation.
        my_to_target = dist(my_pos, top_r)
        opp_separation = dist(my_pos, (ox, oy))
        val = lead * 1000 - my_to_target * 10 + opp_separation
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]