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
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def is_self(x, y): return (x, y) in self_terr
    def is_opp(x, y): return (x, y) in opp_terr
    def adj_to_ours(x, y):
        for dx, dy in dirs:
            if (dx, dy) == (0, 0): 
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in self_terr:
                return True
        return False
    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = [0, 0]
    best_score = -10**18

    # Bias: move toward opponent corner while expanding our frontier.
    # Deterministic tie-break: fixed iteration order in dirs.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        score = 0
        if (nx, ny) == (ox, oy):
            score += 10**9

        if (nx, ny) in resources:
            score += 6000
        if (nx, ny) in unclaimed:
            score += 1800
        if is_opp(nx, ny):
            score += 1200  # flipping enabled on entry

        # Expansion preference
        if adj_to_ours(nx, ny):
            score += 500

        # Avoid getting "stuck" by preferring steps that reduce distance to a useful target:
        # choose nearest unclaimed/opp cell direction heuristically via opponent distance reduction.
        score += 2 * manhattan(nx, ny, ox, oy) * (-1)  # closer to opponent => more score
        score += 3 * (nx - sx) + 1 * (ny - sy)  # gradually push outward toward opponent side

        # Safety: don't linger adjacent to obstacles cluster if it doesn't expand.
        if not adj_to_ours(nx, ny) and (nx, ny) not in unclaimed and (nx, ny) not in resources:
            score -= 150

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best