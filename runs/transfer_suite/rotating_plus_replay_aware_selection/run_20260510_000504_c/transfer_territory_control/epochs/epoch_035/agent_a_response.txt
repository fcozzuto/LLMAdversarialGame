def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_neighbors = set()
    for (x, y) in opp_terr:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) != (x, y):
                opp_neighbors.add((nx, ny))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def center_score(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return -(((x - cx) ** 2) + ((y - cy) ** 2))

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best = (float("-inf"), (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            return [dx, dy]

        s = 0
        if (nx, ny) in resources:
            s += 100000
        elif (nx, ny) in unclaimed:
            s += 60000
        elif (nx, ny) in opp_terr:
            s += 20000
        elif (nx, ny) in self_terr:
            s += 500

        if (nx, ny) in opp_neighbors:
            s += 8000

        # Prefer moving toward opponent when we're behind; otherwise expand toward center/unclaimed.
        myc = int(observation.get("self_territory_count", len(self_terr)))
        opc = int(observation.get("opponent_territory_count", len(opp_terr)))
        behind = 1 if myc < opc else 0
        d_to_opp = manh(nx, ny, ox, oy)
        if behind:
            s += 1200 - 50 * d_to_opp
        else:
            s += 6000 + int(center_score(nx, ny) * 10)
            if (nx, ny) in opp_neighbors:
                s += 2000 - 30 * d_to_opp

        # Mild penalty for being adjacent to obstacles (avoid getting stuck)
        adj_obs = 0
        for kx, ky in dirs:
            ax, ay = nx + kx, ny + ky
            if inb(ax, ay) and blocked(ax, ay):
                adj_obs += 1
        s -= 20 * adj_obs

        # Deterministic tie-break: fixed dir order already provides stability
        if s > best[0]:
            best = (s, (dx, dy))

    return [best[1][0], best[1][1]]