def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_pos = tuple(observation["opponent_position"])
    tx, ty = opp_pos[0], opp_pos[1]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        # Primary: try to flip opponent territory / capture frontier.
        opp_here = 1.0 if cell in opp_terr else 0.0
        uncl_here = 1.0 if cell in unclaimed else 0.0

        adj_opp = 0
        adj_uncl = 0
        adj_self = 0
        for ax, ay in nbrs:
            xx, yy = nx + ax, ny + ay
            if inb(xx, yy):
                t = (xx, yy)
                if t in opp_terr:
                    adj_opp += 1
                elif t in unclaimed:
                    adj_uncl += 1
                elif t in self_terr:
                    adj_self += 1

        # Secondary: pressure the opponent position while staying on our expanding front.
        dist_to_opp = abs(nx - tx) + abs(ny - ty)
        dist_self = abs(nx - sx) + abs(ny - sy)

        val = 0.0
        val += 120.0 * opp_here
        val += 18.0 * uncl_here
        val += 8.0 * adj_opp
        val += 2.0 * adj_uncl
        val += 0.5 * adj_self

        # If we can flip immediately, ignore distance bias; else move toward opp with mild preference for low churn.
        if opp_here < 0.5:
            val += -0.9 * dist_to_opp
            val += -0.05 * dist_self

        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move