def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Find nearest unclaimed distance from a point (small, deterministic scan via min over given list).
    uc_list = list(unclaimed)
    def nearest_unclaimed_dist(x, y):
        if not uc_list:
            return 10**9
        best = 10**9
        for ux, uy in uc_list:
            d = abs(ux - x) + abs(uy - y)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18
    cur_dopp = abs(sx - ox) + abs(sy - oy)
    # tie-break deterministically by preferred direction order
    order = {(-1, 0): 0, (0, -1): 1, (1, 0): 2, (0, 1): 3, (0, 0): 4}

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dopp = abs(nx - ox) + abs(ny - oy)
        dist_uc = nearest_unclaimed_dist(nx, ny)

        score = 0
        if (nx, ny) in unclaimed:
            score += 5000
            # encourage grabbing when it also helps keep away from opponent
            score += (dopp - cur_dopp) * 25
        elif (nx, ny) in my_terr:
            score += 50
            score += (dopp - cur_dopp) * 5
        else:
            score += (dopp - cur_dopp) * 10

        # expansion toward unclaimed
        score += -dist_uc * 3

        # slight preference for moving off edges toward center to avoid being boxed in
        score += -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.1

        if score > best_score or (score == best_score and order[(dx, dy)] < order[best_move]):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]