def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    my_set = set()
    for p in observation.get("self_territory", []) or []:
        try:
            my_set.add((int(p[0]), int(p[1])))
        except:
            pass

    opp_set = set()
    for p in observation.get("opponent_territory", []) or []:
        try:
            opp_set.add((int(p[0]), int(p[1])))
        except:
            pass

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obs_set.add((int(p[0]), int(p[1])))
        except:
            pass

    opp_pos = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    best = (-(10**18), 0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        base = 0.0
        if (nx, ny) in opp_set:
            base += 6.0
        elif (nx, ny) in my_set:
            base -= 1.0
        else:
            base += 2.5

        dist_opp = abs(nx - ox) + abs(ny - oy)
        base -= 0.12 * dist_opp

        # Prefer expanding toward border/frontier (roughly toward opponent corner)
        base += 0.02 * (nx + ny)

        # Small penalty for moving away from nearest of our territory cells (keeps cluster coherent)
        if my_set:
            md = 10**9
            for (tx, ty) in my_set:
                d = abs(tx - nx) + abs(ty - ny)
                if d < md:
                    md = d
                    if md == 0:
                        break
            base -= 0.05 * md

        key = (base, dx, dy)
        if key > best:
            best = key

    return [int(best[1]), int(best[2])]