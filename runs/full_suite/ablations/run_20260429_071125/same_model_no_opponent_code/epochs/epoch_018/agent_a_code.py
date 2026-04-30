def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    occ = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            occ.add((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(px, py):
        return 0 <= px < w and 0 <= py < h

    def valid_step(dx, dy):
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            return False
        if (nx, ny) in occ:
            return False
        return True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    # Pre-filter targets: prefer those not "embedded" by obstacles on both dominant axes
    targets = []
    for p in resources:
        if p is None or len(p) < 2:
            continue
        rx, ry = int(p[0]), int(p[1])
        if not in_bounds(rx, ry):
            continue
        # lightweight obstacle awareness: count how "open" it is
        block = 0
        for sx, sy in [(rx-1, ry), (rx+1, ry), (rx, ry-1), (rx, ry+1)]:
            if (sx, sy) in occ:
                block += 1
        # keep all, but deterministic ordering by openness then coords
        targets.append((block, rx, ry))
    targets.sort(key=lambda t: (t[0], t[1], t[2]))

    for dx, dy in moves:
        if not valid_step(dx, dy):
            continue
        nx, ny = x + dx, y + dy

        # If already on resource tile, keep.
        # (Engine will handle pickup; scoring still favors not stepping into obstacles.)
        step_best = -10**18
        for block, rx, ry in targets[:10]:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Main objective: become first (or widen lead). Tie-break: shorter distance.
            lead = do - ds
            # Secondary objective: avoid pushing into very blocky regions
            openness = -block
            score = lead * 1000 - ds * 10 + openness
            # Small deterministic nudge to break ties toward lower coords
            score += -(rx + ry) * 1e-6
            if score > step_best:
                step_best = score

        if step_best > best_score:
            best_score = step_best
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]