def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def nearest_target_dist(x, y):
        targets = None
        if unclaimed:
            targets = list(unclaimed)
        elif resources:
            targets = list(resources)
        else:
            targets = []
        if not targets:
            return 0
        best = 10**9
        for (tx, ty) in targets[:48]:
            d = manhattan(x, y, tx, ty)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_val = -10**18
    # Prefer expanding and capturing locally; also steer toward unclaimed, slightly toward center.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = 0.0
        cell = (nx, ny)
        if cell in opp_terr:
            val += 6.0
        if cell in unclaimed:
            val += 3.5
        if cell in self_terr:
            val += 0.8
        if cell in resources:
            val += 4.0
        # Distance pressure to nearest unclaimed/resource
        val += -0.6 * nearest_target_dist(nx, ny)
        # Center control bias (contest center against center-claimer)
        val += 0.15 * (-manhattan(nx, ny, cx, cy))
        # Slightly discourage moving away from existing territory boundary
        if self_terr:
            # if surrounded by self, prefer stay
            adj_self = 0
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ax, ay = nx + adx, ny + ady
                if inb(ax, ay) and (ax, ay) in self_terr:
                    adj_self += 1
            val += 0.12 * adj_self
        # Deterministic tie-break: prefer earlier dir order
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]