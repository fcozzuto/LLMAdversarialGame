def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    ox = set()
    for x, y in obstacles:
        ox.add((x, y))

    sx, sy = sp[0], sp[1]
    px, py = op[0], op[1]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = None

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def clamp(v, lo, hi):
        if v < lo: return lo
        if v > hi: return hi
        return v

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in ox:
            continue

        # If any resource is reachable now, strongly prefer the one where we are currently advantaged.
        my_pos = (nx, ny)
        opp_pos = (px, py)

        if resources:
            best_margin = -10**9
            best_r = None
            for rx, ry in resources:
                rpos = (rx, ry)
                dm = dist(my_pos, rpos)
                do = dist(opp_pos, rpos)
                margin = do - dm  # positive means we are closer
                if margin > best_margin:
                    best_margin = margin
                    best_r = rpos
        else:
            best_margin = 0
            best_r = None

        # Compute objective: prioritize winning resources (positive margin), then reduce our distance to that target.
        # Also lightly discourage moving toward being closer to opponent by cutting their progress.
        if best_r is not None:
            my_d = dist(my_pos, best_r)
            opp_d = dist(opp_pos, best_r)
        else:
            my_d = 0
            opp_d = dist(opp_pos, (nx, ny))

        # Blocking/pressure: prefer increasing distance to opponent while still going for the target.
        opp_to_me_before = dist((sx, sy), opp_pos)
        opp_to_me_after = dist(my_pos, opp_pos)
        pressure = (opp_to_me_after - opp_to_me_before)

        val = (best_margin * 1000) - (my_d * 5) + (pressure * 2) - (opp_d * 1)

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]