def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def n8(x, y):
        res = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        res.append((nx, ny))
        return res

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    best_frontier = None
    best_frontier_d = None
    for uc in unclaimed:
        if any(p in opp_t for p in n8(uc[0], uc[1])):
            d = dist((sx, sy), uc)
            if best_frontier_d is None or d < best_frontier_d or (d == best_frontier_d and uc < best_frontier):
                best_frontier_d = d
                best_frontier = uc

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            candidates.append(((dx, dy), -10**9))
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 220  # flipping opponent control
        if (nx, ny) in unclaimed:
            score += 140  # claim unclaimed
        if (nx, ny) in self_t:
            score += 10

        adj_opp = 0
        adj_uncl = 0
        adj_obs = 0
        for px, py in n8(nx, ny):
            if (px, py) in opp_t:
                adj_opp += 1
            if (px, py) in unclaimed:
                adj_uncl += 1
            if (px, py) in obstacles:
                adj_obs += 1

        score += 25 * adj_opp
        score += 6 * adj_uncl
        score -= 3 * adj_obs

        if best_frontier is not None:
            score -= 2 * dist((nx, ny), best_frontier)

        # Encourage spreading rather than hugging a single cell
        if (nx, ny) not in self_t:
            score += 8

        candidates.append(((dx, dy), score))

    candidates.sort(key=lambda t: (t[1], -abs(t[0][0]) - abs(t[0][1]), t[0][0], t[0][1]))
    dx, dy = candidates[-1][0]
    return [int(dx), int(dy)]