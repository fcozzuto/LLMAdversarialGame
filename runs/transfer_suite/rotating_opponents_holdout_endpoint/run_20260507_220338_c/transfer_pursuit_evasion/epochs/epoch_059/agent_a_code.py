def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("avoid" in role_s) or ("runner" in role_s) or ("flee" in role_s)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                m += 1
        return m

    best_delta = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (not inb(nx, ny)) or ((nx, ny) in blocked):
            nx, ny = sx, sy

        dist = cheb(nx, ny)
        mob = mobility(nx, ny)

        adj_obs = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            axx, ayy = nx + ax, ny + ay
            if inb(axx, ayy) and (axx, ayy) in blocked:
                adj_obs += 1

        # Score: evade maximizes distance; pursue minimizes distance.
        # Penalties: adjacent obstacles, low mobility.
        if is_evader:
            score = dist * 10 + mob - adj_obs * 2
        else:
            score = (-dist) * 10 + mob - adj_obs * 2

        if best_score is None or score > best_score:
            best_score = score
            best_delta = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer non-staying if possible, then lexicographic
            if best_delta == [0, 0] and [dx, dy] != [0, 0]:
                best_delta = [dx, dy]
            elif [dx, dy] < best_delta:
                best_delta = [dx, dy]

    return [int(best_delta[0]), int(best_delta[1])]