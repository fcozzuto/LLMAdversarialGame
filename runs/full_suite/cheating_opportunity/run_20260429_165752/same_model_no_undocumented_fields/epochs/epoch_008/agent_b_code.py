def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for r in resources:
        try:
            res.append((int(r[0]), int(r[1])))
        except Exception:
            pass
    obs = set()
    for o in obstacles:
        try:
            obs.add((int(o[0]), int(o[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    if (x, y) in res:
        return [0, 0]

    # If no resources, try to avoid obstacles and slowly move to opponent's side deterministically
    if not res:
        for dx, dy in [(1, 1), (1, 0), (0, 1), (0, 0), (1, -1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    res_set = set(res)
    # Core heuristic: maximize contest advantage against opponent for the best contested resource
    best = None  # (score, tie, dx, dy)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue

        # If move steps directly onto a resource, strongly prefer it (unless blocked already)
        if (nx, ny) in res_set:
            return [dx, dy]

        best_adv = None  # we want opponent farther than us: (do - ds)
        closest_self = None
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if best_adv is None or adv > best_adv:
                best_adv = adv
            # also track self closeness as secondary tie
            if closest_self is None or ds < closest_self:
                closest_self = ds

        # Convert to primary score: prefer positive advantage, but also prefer maximizing adv overall
        # tie-break: smaller closest_self, then deterministic move order index
        tie_self = closest_self if closest_self is not None else 0
        score = best_adv
        order = moves.index((dx, dy))
        candidate = (score, -tie_self, -order, dx, dy)
        if best is None or candidate > best:
            best = candidate

    if best is not None:
        return [best[3], best[4]]

    return [0, 0]