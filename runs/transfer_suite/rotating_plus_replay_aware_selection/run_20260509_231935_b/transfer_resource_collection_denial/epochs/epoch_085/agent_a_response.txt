def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for p in resources:
        if p and len(p) >= 2:
            rx, ry = p[0], p[1]
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**18

    # Precompute opponent "race" distances to each resource
    opp_d = {}
    for rx, ry in res:
        opp_d[(rx, ry)] = cheb(ox, oy, rx, ry)

    # If no resources, move to increase distance from opponent while respecting obstacles
    if not res:
        best_sep = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            sep = cheb(nx, ny, ox, oy)
            if sep > best_sep or (sep == best_sep and (dx, dy) < tuple(best_move)):
                best_sep = sep
                best_move = [dx, dy]
        return best_move

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Greedy "race" advantage: prioritize resources where we can arrive no later than opponent
        score = 0
        for rx, ry in res:
            d_you = cheb(nx, ny, rx, ry)
            d_opp = opp_d[(rx, ry)]
            diff = d_opp - d_you  # positive => we are closer/equal
            if diff >= 0:
                # Strongly prefer immediate collection and near-term guarantees
                score += 1000 * diff - 2 * d_you
            else:
                # Mild penalty for moving away from resources opponent can grab first
                score -= 3 * (-diff) + d_you

        # Secondary: avoid stepping into positions that are strictly worse for all races
        # (tie-break with own nearest distance after move, and then deterministic direction order)
        nearest_you = min(cheb(nx, ny, rx, ry) for rx, ry in res)

        if (score > best_score or
            (score == best_score and (nearest_you < min(cheb(best_move[0] + sx, best_move[1] + sy, rx, ry) for rx, ry in res)))):
            best_score = score
            best_move = [dx, dy]

    # Deterministic final fallback if all filtered out
    return best_move if best_move is not None else [0, 0]