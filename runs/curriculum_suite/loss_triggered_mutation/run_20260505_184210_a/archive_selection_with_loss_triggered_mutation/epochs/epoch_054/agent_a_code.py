def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    # Choose deterministic "focus" resource for each agent: min (distance, x, y) from their corner.
    opp_target = min(resources, key=lambda r: (man(opp, r), r[0], r[1]))
    my_target = min(resources, key=lambda r: (man(me, r), r[0], r[1]))

    # Compute a simple set of opponent shortest-path "signature" cells along Manhattan rectangle.
    # For a move to be considered blocking, it should lie on the monotone region towards opp_target.
    xt, yt = opp_target
    def on_opp_monotone_rect(px, py):
        if px == xt and py == yt:
            return True
        if sx == px and sy == py:
            return True
        # Monotone directions from opp to target: x between, y between, and move is not away in both axes.
        if ox <= px <= xt or xt <= px <= ox:
            if oy <= py <= yt or yt <= py <= oy:
                return True
        return False

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        pos = (nx, ny)
        d_me = man(pos, my_target)
        d_opp = man(pos, opp_target)

        # Prefer getting resources; but also avoid giving opponent easy tempo to their target by "blocking" space.
        # Blocking heuristic: being closer to opp_target along axes reduces their flexibility.
        block = 0
        if on_opp_monotone_rect(nx, ny):
            # If our move decreases opp's distance to target, it's bad unless it also increases their "detour" by taking the corridor.
            # Use sign-sensitive penalties.
            if man(me, opp_target) > man(pos, opp_target):
                block = -1
            else:
                block = 1

        # Secondary: prefer moving towards center when tied, to improve future interception angles.
        center = (w // 2, h // 2)
        d_center = man(pos, center)

        # Composite score: lower is better (deterministic tie-breaking)
        # Emphasize resource progress first, then blocking, then distance to opponent target.
        key = (d_me, d_opp, -block, d_center, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]