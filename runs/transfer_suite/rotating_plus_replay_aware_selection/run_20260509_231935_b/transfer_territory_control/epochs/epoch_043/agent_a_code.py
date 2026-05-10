def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def clamp_cell(x, y):
        if x < 0 or x >= w or y < 0 or y >= h:
            return sx, sy
        return x, y

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    opp_adj = set()
    for (x, y) in opp_terr:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) in unclaimed or (nx, ny) in self_terr or (nx, ny) in opp_terr:
                    opp_adj.add((nx, ny))

    self_adj = set()
    for (x, y) in self_terr:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                self_adj.add((nx, ny))

    self_front = list(self_adj) if self_adj else list(unclaimed)
    opp_front = list(opp_adj) if opp_adj else list(unclaimed)

    turn = int(observation.get("turn_index", 0))
    rot = turn % len(dirs)
    dirs = dirs[rot:] + dirs[:rot]

    candidates = []
    # Local target bias: prefer unclaimed near opponent front; else near self front.
    if opp_front:
        tp = opp_front[(turn * 7) % len(opp_front)]
    elif self_front:
        tp = self_front[(turn * 11) % len(self_front)]
    else:
        tp = (sx, sy)

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = clamp_cell(sx + dx, sy + dy)
        cell = (nx, ny)
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
            cell = (sx, sy)
            dx, dy = 0, 0

        score = 0.0
        if cell in opp_terr:
            score += 140.0
        if cell in unclaimed:
            score += 45.0
        if cell in self_terr:
            score += 8.0
        if cell in self_adj:
            score += 28.0
        if cell in opp_adj and cell in unclaimed:
            score += 20.0

        score += 6.0 / (1.0 + dist_cheb(cell, tp))

        # Make it hard for opponent: move away from them unless contesting opp_adj.
        away = dist_cheb(cell, (ox, oy))
        score += 0.9 * away
        if cell in opp_adj:
            score -= 0.6 * away

        # Mild preference for staying within bounds and not oscillating too much.
        if (nx, ny) == (sx, sy):
            score -= 3.0

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]