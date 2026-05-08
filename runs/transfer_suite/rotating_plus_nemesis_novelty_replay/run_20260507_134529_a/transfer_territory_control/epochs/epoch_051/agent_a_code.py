def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (w - 1, h - 1)))

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    opp_list = list(opp_terr) if opp_terr else [(ox, oy)]

    def adj_count_to_opponent(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    c += 1
        return c

    best = None
    best_v = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            v = -10**9
        else:
            v = 0
            if (nx, ny) in opp_terr:
                v += 120
            elif (nx, ny) in unclaimed:
                v += 50
            elif (nx, ny) in self_terr:
                v += 15
            # Intercept/deny: favor being closer to opponent territory, and closer to its boundary.
            dmin = 10**9
            for fx, fy in opp_list:
                d = abs(nx - fx) + abs(ny - fy)
                if d < dmin:
                    dmin = d
                    if dmin == 0:
                        break
            v += (30 - dmin)
            v += 8 * adj_count_to_opponent(nx, ny)
            # Mild bias: move away from opponent if we can't threaten.
            if (nx, ny) not in opp_terr:
                v -= 0.6 * (abs(nx - ox) + abs(ny - oy))
        if v > best_v or (v == best_v and (dx, dy) < best):
            best_v = v
            best = (dx, dy)
    return [best[0], best[1]]