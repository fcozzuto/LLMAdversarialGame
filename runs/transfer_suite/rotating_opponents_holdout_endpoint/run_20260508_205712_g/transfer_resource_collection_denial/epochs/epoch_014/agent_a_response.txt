def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = [tuple(r) for r in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my = (sx, sy)
    opp = (ox, oy)
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my2 = (nx, ny)

        best_lead = -10**9
        best_tie = 10**9
        best_dS = 10**9

        for r in resources:
            if r in obstacles:
                continue
            dS = cheb(my2, r)
            dO = cheb(opp, r)
            lead = dO - dS
            if lead > best_lead or (lead == best_lead and dS < best_tie):
                best_lead, best_tie, best_dS = lead, dS, dS

        # Value: strongly prefer moves that secure resource races; then closeness.
        # Also softly penalize being too close to opponent overall (helps avoid giving races).
        opp_dist = cheb(my2, opp)
        val = (best_lead * 1000) - best_dS - (1.0 / (1 + opp_dist)) * 10

        # If we can immediately match an opponent race (lead==0), prefer moves that are closest to that resource.
        if best_lead == 0:
            val -= best_dS * 0.5

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]