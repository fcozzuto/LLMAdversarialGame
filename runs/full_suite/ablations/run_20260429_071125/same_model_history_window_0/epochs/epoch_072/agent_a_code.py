def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    x, y = observation['self_position']
    ox, oy = observation['opponent_position']
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    resources = [tuple(p) for p in observation.get('resources', [])]
    if not resources:
        return [0, 0]

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Candidate next positions
    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    cur = (x, y)
    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append(((nx, ny), dx, dy))
    if not candidates:
        return [0, 0]

    opp = (ox, oy)
    # Choose target with opponent-aware advantage
    # Score resources by (my_distance - opp_distance), prefer those where we are closer.
    res_scored = []
    for r in resources:
        myd = man(cur, r)
        opd = man(opp, r)
        # add slight penalty if resource is "behind" opponent direction to diversify targeting
        res_scored.append((myd - opd, myd, opd, r[0], r[1], r))
    res_scored.sort(key=lambda t: (t[0], t[1], t[4], t[3]))
    # If opponent is significantly closer to the closest resource, shift to second/third.
    target = res_scored[0][-1]
    if len(res_scored) > 1 and res_scored[0][0] > -1 and res_scored[0][0] <= 2:
        target = res_scored[1][-1] if (res_scored[1][0] <= res_scored[0][0] - 1) else (res_scored[min(2, len(res_scored)-1)][-1])

    # If opponent is adjacent to a resource, contest that resource deterministically.
    for r in resources:
        if man(opp, r) == 1:
            target = r
            break

    # Evaluate candidates: minimize distance to target, avoid moving away from any resource cluster near obstacles
    best = None
    best_key = None
    for pos, dx, dy in candidates:
        nd = man(pos, target)
        # discourage stepping toward opponent unless it also helps target
        oppd = man(pos, opp)
        # obstacle proximity penalty (stay away from tight corridors)
        ox_pen = 0
        for ox2, oy2 in obstacles:
            d = abs(pos[0]-ox2) + abs(pos[1]-oy2)
            if d == 1:
                ox_pen += 3
            elif d == 2:
                ox_pen += 1
        # primary: reach/approach target; secondary: keep distance from opponent; tertiary: lexicographic stability
        key = (nd, -oppd, ox_pen, pos[0], pos[1])
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]