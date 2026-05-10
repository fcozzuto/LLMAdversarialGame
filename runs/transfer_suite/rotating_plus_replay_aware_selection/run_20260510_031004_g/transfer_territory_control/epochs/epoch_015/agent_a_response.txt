def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = set(map(tuple, observation.get("resources", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    un_list = list(unclaimed)
    opp_list = list(opp_terr)

    def min_dist_to(cells, x, y):
        m = 10**9
        for cx, cy in cells:
            d = abs(cx - x) + abs(cy - y)
            if d < m:
                m = d
        return m if m != 10**9 else 9999

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_terr:
            # immediate counter-claim / flip
            score = 6000
            score += max(0, 20 - (abs(nx - px) + abs(ny - py))) * 3
            score -= max(0, 20 - (abs(nx - sx) + abs(ny - sy)))
        else:
            score = 0
            if (nx, ny) in unclaimed:
                score += 320
            if (nx, ny) in resources:
                score += 140
            if (nx, ny) in self_terr:
                score -= 25

            if un_list:
                score += max(0, 120 - 8 * min_dist_to(un_list, nx, ny))
            if opp_list:
                # keep some distance while expanding
                score -= max(0, 120 - 8 * min_dist_to(opp_list, nx, ny))

            score += - (abs(nx - px) + abs(ny - py)) // 2

        tie = (score, -dx, -dy)
        if best is None or tie > best[0]:
            best = (tie, [dx, dy])

    return best[1] if best is not None else [0, 0]