def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", None) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources", None) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    def valid_move(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # Deterministic tie-break preference order: prefer (0,0), then increasing dx, then increasing dy.
    def move_key(d):
        dx, dy = d
        return (0 if (dx == 0 and dy == 0) else 1, dx + 1, dy + 1)

    best_move = None
    best_score = -10**18

    for dx, dy in sorted(dirs, key=move_key):
        nx, ny = sx + dx, sy + dy
        # If invalid, engine keeps position; incorporate that by treating as staying.
        if not valid_move(nx, ny):
            nx, ny = sx, sy

        # If we can collect immediately, prioritize it strongly.
        if (nx, ny) in res_set:
            score = 10**9
        else:
            score = -10**6

        # Choose resource target deterministically by scoring advantage and closeness.
        # Advantage: (opp_dist - self_dist) higher is better.
        # Also discourage moving away from opponent slightly to prevent deadlocks.
        for r in resources:
            sd = man((nx, ny), r)
            od = man((ox, oy), r)
            adv = od - sd
            # Weights tuned for urgency: immediate reach handled above.
            score += 1200 * (adv > 0) + 40 * adv - 8 * sd
            # Small tie-break: prefer moving towards a globally best (lexicographically stable) resource.
            if r == min(resources):
                score += 2 * adv

        # Additional small term: reduce distance to opponent to contest better.
        score += -0.5 * man((nx, ny), (ox, oy))

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]