def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position") or (sx, sy)
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) == (sx, sy):
            return -0.5
        # Prefer taking opponent or unclaimed; otherwise extend toward opponent.
        if (nx, ny) in opp_terr:
            base = 18.0
        elif (nx, ny) in unclaimed:
            base = 8.0
        elif (nx, ny) in self_terr:
            base = 2.0
        else:
            base = 0.4

        # Distance shaping: move closer to opponent.
        dist_opp = abs(nx - ox) + abs(ny - oy)
        near = 6.0 / (1 + dist_opp)

        # Prefer stepping to cells adjacent to opponent territory (frontier).
        frontier = 0.0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if (ax, ay) in opp_terr:
                    frontier = 2.5
        return base + near + frontier

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            cand.append((step_score(nx, ny), dx, dy))

    # Deterministic tie-break: higher score, then lexicographically smaller (dx,dy).
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [cand[0][1], cand[0][2]] if cand else [0, 0]