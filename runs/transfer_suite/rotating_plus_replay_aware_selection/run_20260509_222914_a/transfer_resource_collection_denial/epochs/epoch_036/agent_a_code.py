def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resset = set()
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            res.append((px, py))
            resset.add((px, py))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-dir shortest

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        # No visible resources: hold line by minimizing being closer to opponent.
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            # Prefer moves that increase opponent distance or keep it while not advancing too much toward them.
            v = dist(nx, ny, ox, oy) - 0.2 * dist(nx, ny, w - 1 - x, h - 1 - y)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        # Race metric: we want resources where we are not worse than opponent, and especially immediate grabs.
        immediate = 1.0 if (nx, ny) in resset else 0.0
        score = -1e9
        for rx, ry in res:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Self priority: closer first, but heavily prefer cells where opponent is farther.
            v = (do - ds) * 3.0 - ds * 1.2
            if v > score:
                score = v
        # Also add small preference to keep distance if tie in resource priority.
        score += immediate * 50.0 + dist(nx, ny, ox, oy) * 0.05
        if score > bestv:
            bestv = score
            best = [dx, dy]
    return best