def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            sc = -man(nx, ny, cx, cy)
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_sc = -10**18
    best_move = [0, 0]
    late = turns_remaining <= 8

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # race scoring over resources: prefer those we can reach sooner and keep away from opponent
        score = 0
        min_ds = 10**9
        min_do = 10**9
        closest_r = None

        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < min_ds:
                min_ds = ds
                closest_r = (rx, ry)
            if do < min_do:
                min_do = do

            if ds == 0:
                score += 10**9
            # primary: win resource before opponent
            diff = do - ds
            score += diff * 250
            # secondary: closer is better
            score += -ds * 10

            # if opponent is about to grab same resource, penalize
            if do <= 1 and ds > 1:
                score -= 900
            if do <= 2 and ds > 3:
                score -= 200

            # discourage moving into opponent's immediate neighborhood
            if man(nx, ny, ox, oy) <= 1:
                score -= 60

        # If late game, prioritize finishing near resources even if contesting
        if late and closest_r is not None:
            score += -min_ds * 30

        if score > best_sc:
            best_sc = score
            best_move = [dx, dy]

    # deterministic tie-break: smallest (dx,dy) lex among equals
    if best_sc == -10**18:
        return [0, 0]
    return best_move