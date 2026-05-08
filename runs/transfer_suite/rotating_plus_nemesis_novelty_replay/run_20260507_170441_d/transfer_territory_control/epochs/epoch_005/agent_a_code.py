def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y):
                obs_set.add((x, y))
        except:
            pass

    def to_set(lst):
        s = set()
        for p in lst or []:
            try:
                x, y = int(p[0]), int(p[1])
                if in_bounds(x, y):
                    s.add((x, y))
            except:
                pass
        return s

    self_set = to_set(observation.get("self_territory", []))
    opp_set = to_set(observation.get("opponent_territory", []))
    un_set = to_set(observation.get("unclaimed_cells", []))
    if not un_set:
        un_set = to_set(observation.get("resources", []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        gain = 0
        if (nx, ny) in opp_set:
            gain = 2  # immediate counterclaim
        elif (nx, ny) in un_set or (nx, ny) not in self_set and (nx, ny) not in obs_set:
            gain = 1  # plausible expansion
        opp_dist = abs(nx - ox) + abs(ny - oy)
        frontier_dist = 10**9
        if un_set:
            for ux, uy in un_set:
                if (abs(ux - nx) <= 1 and abs(uy - ny) <= 1):
                    frontier_dist = 0
                    break
            if frontier_dist > 0:
                for ux, uy in un_set:
                    if any((ux + ax, uy + ay) in opp_set for ax in (-1, 0, 1) for ay in (-1, 0, 1) if not (ax == 0 and ay == 0)):
                        frontier_dist = min(frontier_dist, abs(ux - nx) + abs(uy - ny))
        score = (gain, -opp_dist, -frontier_dist)
        candidates.append((score, [dx, dy]))

    if candidates:
        candidates.sort(key=lambda t: (t[0][0], t[0][1], t[0][2]))
        return candidates[-1][1]

    # fallback: head toward opponent if no targets
    best = [0, 0]
    bestd = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        if d < bestd:
            bestd = d
            best = [dx, dy]
    return best