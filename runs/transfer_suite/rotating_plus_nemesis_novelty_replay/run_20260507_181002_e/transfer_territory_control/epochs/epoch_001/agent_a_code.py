def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]

    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", [])
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells", [])
    resources = observation.get("resources", [])

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        d_op = man(nx, ny, ox, oy)

        score = 0
        if unclaimed:
            d_min = 10**9
            for c in unclaimed:
                try:
                    ux, uy = c[0], c[1]
                except:
                    continue
                d = man(nx, ny, ux, uy)
                if d < d_min:
                    d_min = d
            score = -d_min
        elif resources:
            d_min = 10**9
            for r in resources:
                try:
                    rx, ry = r[0], r[1]
                except:
                    continue
                d = man(nx, ny, rx, ry)
                if d < d_min:
                    d_min = d
            score = -d_min
        else:
            score = -d_op  # fallback

        # Tie-breaker: prefer slightly closer to opponent if no unclaimed/resources
        if unclaimed or resources:
            score += -0.001 * d_op

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]