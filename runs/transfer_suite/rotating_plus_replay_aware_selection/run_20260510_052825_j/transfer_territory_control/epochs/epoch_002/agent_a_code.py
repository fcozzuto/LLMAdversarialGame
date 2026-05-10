def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation.get("opponent_position", (x, y))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def cheb(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    un_list = list(unclaimed)
    opp_list = list(oppT) if oppT else [(ox, oy)]
    my_list = list(selfT) if selfT else [(x, y)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0); bestv = -10**18

    # Deterministic mode switch to avoid repeating same approach
    mode = 1 if (observation.get("turn_index", 0) % 4) in (0, 2) else 0

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        pos = (nx, ny)

        v = 0
        d_to_opp = min(cheb(pos, t) for t in opp_list)
        d_to_me = min(cheb(pos, t) for t in my_list)

        if pos in oppT:
            v += 260 + (2 if mode else 0) * 20
            v += 25 * (d_to_me == 0)  # prefer flipping while still near our held area
        elif pos in unclaimed:
            v += 210
        elif pos in selfT:
            v += 70

        # If we can raid immediately, prioritize it strongly (territory flipping on entry)
        if d_to_opp <= 1:
            v += 300 - 40 * d_to_opp

        if un_list:
            dmin = min(cheb(pos, t) for t in un_list)
            # Alternate between expansion and interception
            if mode == 0:
                v += 220 - 18 * dmin
                v += -40 * (min(cheb((ox, oy), t) for t in un_list) - dmin)
            else:
                # Intercept: prefer targets that opponent is close to (we can steal them)
                dopp = min(cheb((ox, oy), t) for t in un_list)
                v += (dopp - dmin) * 35
                v += 130 - 12 * dmin
        else:
            # No unclaimed info: keep pressure near the diagonal toward opponent corner
            v += 40 * (d_to_me - d_to_opp)
            v += -10 * cheb(pos, (ox, oy))

        if v > bestv:
            bestv = v; best = (dx, dy)

    return [int(best[0]), int(best[1])]