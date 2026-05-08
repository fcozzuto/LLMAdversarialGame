def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    frontier_unclaimed = []
    if unclaimed and self_terr:
        for (x, y) in unclaimed:
            for dx, dy in neigh8:
                if (x + dx, y + dy) in self_terr:
                    frontier_unclaimed.append((x, y))
                    break

    targets = frontier_unclaimed if frontier_unclaimed else list(unclaimed) if unclaimed else list(opp_terr) if opp_terr else [(w // 2, h // 2)]

    def best_next_cell():
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            cell = (nx, ny)

            # Determine immediate payoff / risk
            if cell in unclaimed:
                t = 30
            elif cell in self_terr:
                t = 6
            elif cell in opp_terr:
                t = 18
            else:
                t = 0

            # Prefer capturing cells close to "good" targets, but also avoid walking straight into opponent pressure
            d_t = min((man(nx, ny, tx, ty) for (tx, ty) in targets), default=0)
            d_o = man(nx, ny, ox, oy)

            # Extra bias: if opponent is near, don't step into their territory unless it moves us toward frontier targets
            risk = 0
            if cell in opp_terr and d_o <= man(sx, sy, ox, oy) + 1:
                risk = 10

            # Prefer increasing distance from opponent when no capture is possible
            if cell not in unclaimed and cell not in opp_terr:
                risk += (7 - min(d_o, 7))

            score = t + 20 - d_t - risk
            cand = (score, -d_o, dx, dy, nx, ny)
            if best is None or cand > best:
                best = cand
        return best[2:4] if best else (0, 0)

    dx, dy = best_next_cell()
    return [int(dx), int(dy)]